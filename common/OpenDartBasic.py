import dart_fss as dart
import urllib.request as ul
from zipfile import ZipFile
from io import BytesIO
import xml.etree.ElementTree as elemTree
import json
import pandas as pd


# API 키를 할당하고 인증 받는 절차
def api_key(api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'):
    dart.set_api_key(api_key=api_key)
    return api_key


# url을 입력하면 json형태로 온 "list" 응답결과를 dict로 반환해주는 코드. 정보를 dict로 추출해온 후, pandas DataFrame 객체로 반환한다.
def get_info_from_url(url):
    request = ul.Request(url)
    response = ul.urlopen(request)
    responseData = response.read()
    data = json.loads(responseData)
    if data['status'] == '000':
        response = pd.json_normalize(data['list'])
    elif data['status'] == '013':
        # 검색한 정보가 없을 때
        return 13
    elif data['status'] == '010':
        # 등록되지 않은 키
        return 10
    elif data['status'] == '011':
        # 사용할 수 없는 키입니다. 오픈API에 등록되었으나, 일시적으로 사용 중지된 키를 통하여 검색하는 경우 발생합니다.
        return 11
    elif data['status'] == '020':
        # 요청 제한을 초과
        return 20
    elif data['status'] == '100':
        # 필드의 부적절한 값입니다. 필드 설명에 없는 값을 사용한 경우에 발생하는 메시지입니다.
        return 100
    elif data['status'] == '800':
        # 원활한 공시서비스를 위하여 오픈API 서비스가 중지 중입니다.
        return 800
    elif data['status'] == '900':
        # 정의되지 않은 오류가 발생하였습니다.
        return 900
    else:
        # 이외의 원인을 알 수 없는 오류들
        return -1

    return response

# request_url: 요청 url 형태, condition_info: get_url_info의 반환값. 조건에 맞는 url을 string으로 반환한다.
def get_url(api_key, request_url, condition_info={}):
    url = request_url+"?crtfc_key="+api_key
    for condition in condition_info:
        condition_info[condition] = "&"+condition+"="+condition_info[condition]
    for condition in condition_info:
        url += condition_info[condition]
    return url



##기업의 이름으로 고유번호를 가져오기 위한 함수들. get_corp_code_by_name만 호출하면 가져올 수 있다.
# 기업 이름으로 검색 후, 고유번호 8자리를 반환. api_key를 input으로 넣는다. 약간만 조작하면 stock_code값과 modify_date도 가져올 수 있는 함수.
def get_corp_code_by_name(api_key):
    corp_name = input("검색할 기업의 이름 입력: ")
    print("전체 기업 리스트 로딩 중...\n")
    corp_list = update_corp_list(api_key)
    try:
        condition = (corp_list['corp_name'] == corp_name)
        result = corp_list[condition]
        result_np = result.values
        if len(result_np) == 1:
            return result_np[0,1]
        if len(result_np) > 1:    # 동일한 기업이 두 개 이상일 경우, 기업 분류로 다시 판별하여 corp_code를 가져온다.
            usr_corp_cls = input("검색한 기업이 두 개 이상입니다. 기업 유형을 선택해주세요. 유가는 'Y', 코스닥은 'K', 코넥스는 'N', 기타는 'E' 입력:\n")
            for comp_info in result_np:
                url = get_url(api_key, "https://opendart.fss.or.kr/api/company.json", {'corp_code' : comp_info[1]})
                request = ul.Request(url)
                response = ul.urlopen(request)
                responseData = response.read()
                data = json.loads(responseData)
                if data["corp_cls"] == usr_corp_cls:
                    return data["corp_code"]
                else:
                    continue
            print("검색한 기업이 존재하지 않습니다. 다시 입력하세요.\n")
            return get_corp_code_by_name(api_key)
    except IndexError:
        print("검색한 기업이 존재하지 않습니다. 다시 입력하세요.\n")
        return get_corp_code_by_name(api_key)


# url을 입력하면 xml 형태로, 맨 첫 기업 정보 로드에 필요한 정보를 pandans DataFrame 객체로 반환해주게 된다.
def load_company_lists(url):
    request = ul.Request(url)
    response = ul.urlopen(request)

    with ZipFile(BytesIO(response.read())) as zf:
        file_list = zf.namelist()
        while len(file_list) > 0:
            file_name = file_list.pop()
            corpCode = zf.open(file_name).read().decode()

    tree = elemTree.fromstring(corpCode)

    XML_stocklist = tree.findall("list")
    corp_name = [x.findtext("corp_name") for x in XML_stocklist]
    corp_code = [x.findtext("corp_code") for x in XML_stocklist]
    stock_code = [x.findtext("stock_code") for x in XML_stocklist]

    dicts_of_dc_info = []

    for i in range(len(corp_code)):
        dicts_of_dc_info.append({
            'corp_name':corp_name[i],
            'corp_code':corp_code[i],
            'stock_code':stock_code[i],
        })

    col_name = []
    rows = []

    for info in dicts_of_dc_info[0]:
        col_name.append(info)

    for infos in dicts_of_dc_info:
        row = []
        for info in infos:
            row.append(infos[info])
        rows.append(row)
    response = pd.DataFrame(rows, columns=col_name)
    return response


# 모든 상장된 기업 리스트 불러오기
def update_corp_list(api_key):
    url = "https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key="+api_key
    corp_list = load_company_lists(url)
    return corp_list

