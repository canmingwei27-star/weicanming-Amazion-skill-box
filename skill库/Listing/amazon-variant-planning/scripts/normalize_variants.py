"""Normalize positional variant tables. Standard library only; never edits input."""
import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


def clean(value):
    if value is None:
        return ''
    return ' '.join(unicodedata.normalize('NFKC', str(value)).split())


def header(value):
    return re.sub(r'\s+', '', clean(value)).replace('－', '-').replace('—', '-')


def number(value):
    text = clean(value)
    if not text:
        return None
    try:
        result = Decimal(text)
    except InvalidOperation:
        return None
    return float(result) if result.is_finite() else None


LENGTHS = {'码': ('yd', 0.9144), 'yd': ('yd', 0.9144), 'yard': ('yd', 0.9144), 'yards': ('yd', 0.9144),
           '米': ('m', 1), 'm': ('m', 1), '厘米': ('cm', 0.01), 'cm': ('cm', 0.01),
           '英寸': ('in', 0.0254), 'inch': ('in', 0.0254), 'in': ('in', 0.0254),
           '英尺': ('ft', 0.3048), 'feet': ('ft', 0.3048), 'ft': ('ft', 0.3048)}


def normalize_table(table, corrections=None):
    corrections = corrections or {}
    raw_headers = table['headers']
    headers = [header(h) for h in raw_headers]
    rows = table['rows']
    source = table.get('source', 'unspecified')
    sheet = table.get('sheet')
    all_issues = []
    applied = []
    parsed = []

    for offset, row in enumerate(rows, 2):
        rownum = row.get('row', offset) if isinstance(row, dict) else offset
        values = row['values'] if isinstance(row, dict) else row
        if not any(clean(x) for x in values):
            continue
        ref = {'source': source, 'sheet': sheet, 'row': rownum}
        issues = []
        used = set()
        if len(values) != len(headers):
            issues.append({'code': 'row_width_mismatch', 'expected': len(headers), 'actual': len(values)})

        def at(index):
            return values[index] if index < len(values) else None

        def get(name):
            indices = [i for i, h in enumerate(headers) if h == name]
            if len(indices) > 1:
                issues.append({'code': 'duplicate_scalar_header', 'field': name, 'columns': [i+1 for i in indices]})
            if not indices:
                return None
            used.add(indices[0])
            return at(indices[0])

        def measurement(raw, unit, field, kind=None):
            val = number(raw)
            if clean(raw) and (val is None or val <= 0):
                issues.append({'code': 'invalid_measurement', 'field': field, 'raw': raw})
                val = None
            result = {'value': val, 'unit': unit, 'raw': raw}
            if kind:
                result['kind'] = kind
            return result

        parent = clean(get('父体SKU')) or None
        original_msku = clean(get('MSKU')) or None
        msku = corrections.get(original_msku, original_msku)
        if msku != original_msku:
            applied.append({'old': original_msku, 'new': msku, 'source': ref, 'authority': 'explicit_user_correction'})
        brand = clean(get('品牌')) or None
        category = clean(get('分类')) or None
        attr_label = clean(get('属性')) or None
        actual = clean(get('实际')) or None
        if not parent:
            issues.append({'code': 'missing_parent_sku', 'field': 'parent_sku'})
        if not msku:
            issues.append({'code': 'missing_msku', 'field': 'msku'})
        attrs = []
        for i, h in enumerate(headers):
            match = re.fullmatch(r'属性(\d+)', h)
            if not match:
                continue
            used.add(i)
            axis_id = 'attribute_' + match[1]
            raw = at(i)
            unit_raw = None
            if i + 1 < len(headers) and headers[i+1] in ['属性单位', '属性单位'+match[1]]:
                unit_raw = at(i+1)
                used.add(i+1)
            unit_text = clean(unit_raw)
            val = clean(raw) or None
            if unit_text in ['颜色', '色彩', 'color', 'Color']:
                kind, label, unit, valn = 'color', '颜色', None, val
            elif unit_text.lower() in LENGTHS:
                unit, factor = LENGTHS[unit_text.lower()]
                kind, label, valn = 'length', '长度', number(raw)
                if valn is None or valn <= 0:
                    issues.append({'code': 'invalid_attribute_measurement', 'axis_id': axis_id, 'raw': raw})
                    valn = None
            elif unit_text in ['尺寸', 'size', 'Size']:
                kind, label, unit, valn = 'size', '尺寸', None, val
            elif unit_text in ['数量', '个', '件', '卷', 'pcs', 'pack']:
                kind, label, unit, valn = 'quantity', '数量', unit_text, number(raw)
                if valn is None or valn <= 0:
                    issues.append({'code': 'invalid_attribute_measurement', 'axis_id': axis_id, 'raw': raw})
                    valn = None
            else:
                kind, label, unit, valn = 'unknown', h, unit_text or None, val
                issues.append({'code': 'unknown_attribute_type', 'axis_id': axis_id, 'unit_raw': unit_raw})
            if val is None:
                issues.append({'code': 'missing_attribute', 'axis_id': axis_id})
            attrs.append({'axis_id': axis_id, 'name': label, 'kind': kind, 'value': valn,
                          'value_raw': raw, 'unit': unit, 'unit_raw': unit_raw,
                          'display': ((val or '未提供') + (' '+unit_text if kind in ['length', 'quantity'] else '')),
                          'column': i+1, 'unit_column': i+2 if unit_raw is not None else None})
        price_raw = get('价格(美金)')
        price_val = number(price_raw)
        if clean(price_raw) and (price_val is None or price_val < 0):
            issues.append({'code': 'invalid_price', 'raw': price_raw})
            price_val = None
        dims = {key: measurement(get('包装-'+label+'(inch)'), 'in', 'package_'+key)
                for key, label in [('length','长'),('width','宽'),('height','高')]}
        weight = measurement(get('包装-重量(lb)'), 'lb', 'package_weight', 'package_weight')
        product_weights = []
        for i, h in enumerate(headers):
            match = re.fullmatch(r'(商品重量|商品净重|净重)\((g|kg|lb|oz)\)', h, re.I)
            if match:
                used.add(i)
                kind = 'net_weight' if '净重' in match[1] else 'product_weight_unspecified'
                product_weights.append(measurement(at(i), match[2].lower(), h, kind))
        if len(product_weights) > 1:
            issues.append({'code': 'multiple_product_weight_columns', 'values': product_weights})
        product_weight = product_weights[0] if len(product_weights) == 1 else None
        # SKU suffixes only raise issues; they never supply or override product facts.
        if msku:
            hint = re.search(r'-(\d+(?:\.\d+)?)(Y|YD|M|CM|FT|IN)$', msku, re.I)
            if hint:
                suffix_unit = {'Y':'yd','YD':'yd','M':'m','CM':'cm','FT':'ft','IN':'in'}[hint[2].upper()]
                meters = float(hint[1]) * LENGTHS[suffix_unit][1]
                lengths = [a for a in attrs if a['kind']=='length' and a['value'] is not None]
                if len(lengths)==1:
                    a=lengths[0]
                    if abs(a['value']*LENGTHS[a['unit']][1]-meters)>1e-8:
                        issues.append({'code':'sku_length_conflict','msku':msku,'sku_hint':hint[0], 'attribute':a,'affected_fields':['length','size_copy']})
        if actual:
            match = re.search(r'[*×x]\s*(\d+(?:\.\d+)?)\s*(码|yd|yards?|米|cm|m|英寸|inch|in)(?![A-Za-z])',actual,re.I)
            lengths = [a for a in attrs if a['kind']=='length' and a['value'] is not None]
            if match and len(lengths)==1:
                actual_unit=match[2].lower()
                actual_m=float(match[1])*LENGTHS[actual_unit][1]
                a=lengths[0]
                if abs(actual_m-a['value']*LENGTHS[a['unit']][1])>1e-8:
                    issues.append({'code':'actual_length_conflict','actual':actual,'attribute':a,'affected_fields':['actual_spec','length']})
        extra = [{'column':i+1,'header':raw_headers[i] if i<len(headers) else None,'value':value}
                 for i,value in enumerate(values) if i not in used and clean(value)]
        identity=(parent or '@missing-parent:'+str(rownum),msku or '@missing-msku:'+str(rownum))
        vid='V-'+hashlib.sha256(json.dumps(identity,ensure_ascii=False).encode()).hexdigest()[:16]
        parsed.append({'variant_id':vid,'parent_sku':parent,'msku':msku,'brand':brand,'category_label':category,
                       'attribute_label_raw':attr_label,'attributes':attrs,'actual_spec_raw':actual,
                       'price':{'value':price_val,'currency':'USD','raw':price_raw},'package_dimensions':dims,
                       'package_weight':weight,'product_weight':product_weight,'extras':extra,
                       'sources':[ref],'issues':issues,'status':'needs_review' if issues else 'ready'})

    def signature(record):
        return json.dumps({k:v for k,v in record.items() if k not in ['sources','issues','status']},sort_keys=True,ensure_ascii=False)

    variants=[];seen={};duplicates=[]
    for record in parsed:
        vid=record['variant_id']
        if vid not in seen:
            seen[vid]=record;variants.append(record);continue
        old=seen[vid]
        if signature(old)==signature(record) and not old.get('conflict_records'):
            old['sources']+=record['sources']
            duplicates.append({'variant_id':vid,'msku':record['msku'],'merged_sources':record['sources']})
        else:
            if 'conflict_records' not in old:
                old['conflict_records']=[{k:v for k,v in old.items()}]
                old['issues']=old['issues']+[{'code':'conflicting_msku_records','affected_fields':['variant_record']}]
            old['conflict_records'].append(record)
            old['sources']=old['sources']+record['sources']
            old['status']='needs_review'
    families=[]
    grouped=defaultdict(list)
    for record in variants:
        grouped[record['parent_sku'] or record['variant_id']].append(record)
    for parent, records in grouped.items():
        combos=defaultdict(list)
        for record in records:
            combo=json.dumps([(a['axis_id'],a['kind'],a['value'],a['unit']) for a in record['attributes']],ensure_ascii=False)
            combos[combo].append(record)
        for matches in combos.values():
            if len(matches)>1:
                for record in matches:
                    record['status']='needs_review'
                    record['issues'].append({'code':'ambiguous_combination','mskus':[r['msku'] for r in matches]})
        axes={}
        for record in records:
            for a in record['attributes']:
                axis=axes.setdefault(a['axis_id'],{'axis_id':a['axis_id'],'name':a['name'],'kind':a['kind'],'options':[]})
                opt={'value':a['value'],'unit':a['unit'],'display':a['display']}
                if opt not in axis['options']:axis['options'].append(opt)
        for a in axes.values():a['selectable']=len(a['options'])>1
        families.append({'parent_sku':records[0]['parent_sku'],'variant_ids':[r['variant_id'] for r in records], 'axes':list(axes.values()),'combinations':[{'variant_id':r['variant_id'],'msku':r['msku'],'attributes':r['attributes'],'status':r['status']} for r in records]})
    for record in variants:
        all_issues += [{'variant_id':record['variant_id'],'msku':record['msku'],**i} for i in record['issues']]
    return {'schema_version':1,'source':source,'sheet':sheet,'headers':[{'column':i+1,'raw':h,'normalized':headers[i]} for i,h in enumerate(raw_headers)],
            'raw_rows':rows,'variants':variants,'families':families,'issues':all_issues,'duplicate_groups':duplicates,'corrections':applied,
            'summary':{'input_rows':len(parsed),'unique_variants':len(variants),'merged_duplicate_rows':len(duplicates),'needs_review':sum(r['status']=='needs_review' for r in variants)}}


def load_table(path):
    if path.suffix.lower()=='.csv':
        with path.open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.reader(f))
        return {'source':str(path),'sheet':None,'headers':rows[0],'rows':[{'row':i,'values':row} for i,row in enumerate(rows[1:],2)]}
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('input',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--corrections',type=Path)
    args=parser.parse_args()
    correction=json.loads(args.corrections.read_text(encoding='utf-8-sig')) if args.corrections else {}
    result=normalize_table(load_table(args.input),correction)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['summary'],ensure_ascii=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
