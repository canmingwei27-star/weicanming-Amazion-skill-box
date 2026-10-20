import copy
import unittest
from normalize_variants import normalize_table

HEADERS=['品牌','分类','父体SKU','MSKU','属性','属性1','属性单位','属性2','属性单位','实际','价格（美金）',' 包装-长(inch) ','包装-宽(inch)','包装-高(inch)','包装-重量(lb)']
def table(msku='P-Red-1Y', color='红色', length=1):
    return {'source':'test','headers':HEADERS,'rows':[{'row':2,'values':['Bijou Joon','花边','P',msku,'Red',color,'颜色',length,'码','10CM（流苏长9CM，带宽1CM）*1码',9.99,4.72,4.72,.59,.22]}]}
class Checks(unittest.TestCase):
    def test_duplicate_unit_headers_preserved(self):
        r=normalize_table(table());v=r['variants'][0]
        self.assertEqual([a['kind'] for a in v['attributes']],['color','length'])
        self.assertEqual(v['attributes'][1]['unit'],'yd')
        self.assertEqual(r['headers'][6]['normalized'],r['headers'][8]['normalized'])
    def test_package_weight_not_net_weight(self):
        v=normalize_table(table())['variants'][0]
        self.assertEqual(v['package_weight']['value'],.22)
        self.assertIsNone(v['product_weight'])
        self.assertEqual(v['package_dimensions']['width']['unit'],'in')
    def test_identical_duplicates_merge_and_keep_sources(self):
        t=table();t['rows'].append({'row':8,'values':t['rows'][0]['values'].copy()})
        r=normalize_table(t);self.assertEqual(r['summary']['unique_variants'],1)
        self.assertEqual([x['row'] for x in r['variants'][0]['sources']],[2,8])
    def test_conflicting_msku_never_overwritten(self):
        t=table();row=copy.deepcopy(t['rows'][0]);row['row']=3;row['values'][10]=12.99;t['rows'].append(row)
        v=normalize_table(t)['variants'][0];self.assertEqual(v['status'],'needs_review')
        self.assertEqual(len(v['conflict_records']),2)
    def test_suffix_is_not_fact(self):
        r=normalize_table(table('P-Red-5Y'))
        self.assertIn('sku_length_conflict',[x['code'] for x in r['issues']])
        self.assertEqual(r['variants'][0]['attributes'][1]['value'],1)
    def test_user_correction_removes_suffix_conflict(self):
        t=table('P-Red-5Y');r=normalize_table(t,{'P-Red-5Y':'P-Red-1Y'})
        self.assertFalse(r['issues']);self.assertEqual(r['corrections'][0]['old'],'P-Red-5Y')
        self.assertEqual(r['raw_rows'][0]['values'][3],'P-Red-5Y')
    def test_only_real_combinations(self):
        t=table();b=table('P-Black-5Y','黑色',5)['rows'][0];b['row']=3;b['values'][9]='10CM*5码';t['rows'].append(b)
        f=normalize_table(t)['families'][0];self.assertEqual(len(f['combinations']),2)
        self.assertEqual(len(f['axes'][0]['options']),2);self.assertEqual(len(f['axes'][1]['options']),2)
    def test_actual_length_conflict(self):
        t=table();t['rows'][0]['values'][9]='10CM*5码'
        self.assertIn('actual_length_conflict',[x['code'] for x in normalize_table(t)['issues']])
    def test_net_weight_requires_explicit_column(self):
        t=table();t['headers']=HEADERS+['商品净重(g)'];t['rows'][0]['values'].append(85)
        w=normalize_table(t)['variants'][0]['product_weight'];self.assertEqual(w['value'],85)
        self.assertEqual(w['kind'],'net_weight');self.assertEqual(w['unit'],'g')
    def test_missing_values_remain_missing(self):
        t=table();t['rows'][0]['values'][14]=None
        self.assertIsNone(normalize_table(t)['variants'][0]['package_weight']['value'])
    def test_same_attributes_different_msku_ambiguous(self):
        t=table();row=copy.deepcopy(t['rows'][0]);row['row']=3;row['values'][3]='P-Red-other';t['rows'].append(row)
        r=normalize_table(t);self.assertEqual(r['summary']['unique_variants'],2)
        self.assertEqual(r['summary']['needs_review'],2)
    def test_unknown_attribute_not_assumed_size(self):
        t=table();t['rows'][0]['values'][8]='XUnit'
        r=normalize_table(t);self.assertEqual(r['variants'][0]['attributes'][1]['kind'],'unknown')
        self.assertIn('unknown_attribute_type',[x['code'] for x in r['issues']])
    def test_families_not_cross_joined(self):
        t=table();row=copy.deepcopy(t['rows'][0]);row['row']=3;row['values'][2]='P2';row['values'][3]='P2-Red-1Y';t['rows'].append(row)
        self.assertEqual(len(normalize_table(t)['families']),2)
if __name__=='__main__':unittest.main()
