import pandas as pd
from tabulate import tabulate
import openpyxl

import sys
sys.path.append("/workspace/Stock_Investment_Too/common")

import OpenDartBasic as odb
import OpenDartAPI as oda

api_key = odb.api_key('125cdc5bc1899431fea946a38533cebf51494b54')


# 국채시가배당률을 계산하기 위한 표를 작성하여 DataFrame객체로 반환한다. 이 과정에서 참고하였던 재무제표들도 같이 반환된다.
## most_recent가 'N'이면 가장 최근의 보고서를 반영하지 않는다. 'Y'이면 가장 최근의 보고서를 함께 보여준다.
## stock_knd가 'O'(ordinary stock)이면 보통주 데이터를, 'P'이면 우선주 데이터를 보여준다.
def govern_bond_diviend_rate_table(api_key, most_recent='N', stock_knd='O'):
    corp_code = odb.get_corp_code_by_name(api_key)
    resp_list = []
    if most_recent=='Y':
        pass

    for i in range(2):
        bsns_year = str(2020-i*3)
        response = oda.diviend_infos(api_key, corp_code, bsns_year=bsns_year, reprt_code='11011')
        resp_list.append(response)
    table_data = {'2020년': [],
                 '2019년': [],
                 '2018년': [],
                 '2017년': [],
                 '2016년': [],
                '2015년': []
                }
    
    three_year_govern_bond_rate = {'2015년' : 1.79, '2016년' : 1.44, '2017년' : 1.80, '2018년' : 2.10, '2019년' : 1.53, '2020년' : 0.99}
    
    for i, df in enumerate(resp_list):
        # 불린 인덱싱 컨디션 설정 준비과정
        if type(df) != int:
            eps_cond = (df['se'].str.contains('주당순이익'))
            dps_cond = (df['se'].str.contains('주당 현금배당금'))
            cash_diviend_rate_cond = (df['se'].str.contains('현금배당수익률'))
            stock_diviend_rate_cond = (df['se'].str.contains('주식배당수익률'))
        #불린 인덱싱 컨디션 조건 설정 끝
        
        for j, year_data in enumerate(table_data):
            if i==0 and j<3:    # 첫 번째 df와 두 번째 df에서 각 table_data의 1,2,3번째와 4,5,6번째 key값에만 값을 저장하기 위한 작업.
                index = j
            if i==1 and j>=3:
                index = j-3
            
            if (i==0 and j<3 and type(df)!=int) or (i==1 and j>=3 and type(df)!=int):
                table_data[year_data].append(df[eps_cond].iloc[0,5+index])
                table_data[year_data].append(df[dps_cond].iloc[0,5+index])
                table_data[year_data].append(df[cash_diviend_rate_cond].iloc[0,5+index])
                table_data[year_data].append(three_year_govern_bond_rate[year_data])
                try:    # 만약 배당이 빠진 해가 있었다면, 해당 연도의 국채시가배당률을 구할 수 없음. 이에 대한 예외처리.
                    table_data[year_data].append(round(float(table_data[year_data][2])/float(table_data[year_data][3]),2))
                except ValueError:
                    table_data[year_data].append('-')
            elif (i==0 and j<3 and type(df)==int) or (i==1 and j>=3 and type(df)==int):    # 배당이 당기에 이루어지지 않은 경우에는 status가 013으로, '13'이 반환됨에 따른 예외처리.
                for k in range(3):
                    table_data[year_data].append('-')
                table_data[year_data].append(three_year_govern_bond_rate[year_data])
                table_data[year_data].append('-')
            else:
                continue
    table_df = pd.DataFrame(table_data, index=['주당순이익(원)', '주당배당금(원)', '시가배당률(%)', '3년 국채수익률(%)', '국채시가배당률(배)'])
    return table_df, resp_list[0], resp_list[1]


def print_df_with_tabulate(*dfs):
    for df in dfs:
        sample_df = pd.DataFrame([[1,2], [2,3]], columns=['col1', 'col2'])
        if type(df) == type(sample_df):
            print(tabulate(df, headers='keys', tablefmt='psql'), '\n')


def df_to_excel_file(*dfs):
    with pd.ExcelWriter('/workspace/Stock_Investment_Too/국채시가배당률표.xlsx') as writer:
        for i, df in enumerate(dfs):
            sample_df = pd.DataFrame([[1,2], [2,3]], columns=['col1', 'col2'])
            if type(df) == type(sample_df):
                sheet_name = "sheet%d" % (i+1)
                df.to_excel(writer, sheet_name=sheet_name)


table, finan_stat1, finan_stat2 = govern_bond_diviend_rate_table(api_key)
print_df_with_tabulate(finan_stat1, finan_stat2, table)
df_to_excel_file(finan_stat1, finan_stat2, table)

#resp = heavy_shareholder_status_table(api_key)
#print_df_with_tabulate(resp)