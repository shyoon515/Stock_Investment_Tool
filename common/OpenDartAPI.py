import OpenDartBasic as odb

# 배당에 관한 사항 공시정보 호출 함수. crtfc_key는 api_key 입력, corp_code는 get_corp_code_by_name 호출값, bsns_year는 사업연도(디폴트 2020년이며 2015 이후여야 함), reprt_code는 11013은 1분기 보고서, 11012는 반기보고서, 11014는 3분기보고서, 디폴트로 되어있는 건 사업보고서.
def diviend_infos(crtfc_key, corp_code, bsns_year='2020', reprt_code='11011'):
    condition_info = {'corp_code' : corp_code, 'bsns_year': bsns_year, 'reprt_code': reprt_code}
    request_url = "https://opendart.fss.or.kr/api/alotMatter.json"
    url = odb.get_url(api_key=crtfc_key, request_url=request_url, condition_info=condition_info)
    response = odb.get_info_from_url(url)
    return response


def heavy_shareholder_status(crtfc_key, corp_code, bsns_year='2020', reprt_code='11011'):
    condition_info = {'corp_code' : corp_code, 'bsns_year': bsns_year, 'reprt_code': reprt_code}
    request_url = "https://opendart.fss.or.kr/api/hyslrSttus.json"
    url = odb.get_url(api_key=crtfc_key, request_url=request_url, condition_info=condition_info)
    response = odb.get_info_from_url(url)
    return response