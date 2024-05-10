import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from collections import deque
import time
import re

"""
    Selenium  DOM 접근 Method
    
find_element_by_id(ID)              : id 속성으로 요소 1개 추출
find_element_by_name(NAME)          : name 속성으로 요소 1개 추출
find_element_by_css_selector(QUERY) : CSS 선택자로 요소 1개 추출
find_element_by_xpath(QUERY)        : XPath를 지정해 요소 1개 추출
find_element_by_tag_name(NAME)      : 태그 이름이 NAME에 해당하는 요소 1개 추출
find_element_by_link_text(TEXT)     : 링크 텍스트로 요소 추출
find_element_by_partial_link_text(TEXT) :   링크의 자식 요소에 포함된 텍스트로 요소 1개 추출
find_element_by_class_name(NAME)    : 클래스 이름이 NAME에 해당하는 요소 1개 추출

find_elements_by_css_selector(QUERY): CSS 선택자 요소를 여러 개 추출한다.
find_elements_by_xpath(QUERY)       : XPath를 지정해 요소를 여러 개 추출한다.
find_elements_by_tag_name(NAME)     : 태그 이름이 NAME에 해당하는 요소를 여러 개 추출한다.
find_elements_by_class_name(NAME)   : 클래스 이름이 NAME에 해당하는 요소를 여러 개 추출한다.
find_elements_by_partial_link_text(TEXT) : 링크의 자식 요소에 포함된 텍스트로 요소를 여러 개 추출한다.

※ 어떠한 요소도 찾지 못한다면 NoSuchElementException 예외 발생.

    DOM 요소에 적용하는 Method
    
clear() : 글자를 입력할 수 있는 요소의 글자를 지움.
click() : 요소를 클릭.
submit(): 입력 양식 전송.
location : 요소의 위치.
id      : 요소의 id 속성명.
parent  : 부모 요소.
size    : 요소의 크기.
text    : 요소 내부의 글자.
rect    : 크기와 위치 정보를 가진 딕셔너리 자료형 리턴.
tag_name: 태그 이름.
get_attribute(NAME) : NAME에 해당하는 속성의 값 추출.
is_displayed()      : 요소가 화면에 출력되는지 확인.
is_enabled()        : 요소가 활성화돼 있는지 확인.
is_selected()       : 체크박스 등의 요소가 선택된 상태인지 확인.
screenshot(filename): 스크린샷 저장.
screenshot_as_png   : 스크린샷을 PNG 형식의 바이너리로 추출.
send_keys(value)    : 키를 입력.
    

"""

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# Chrome 공식 버전 : 123.0.6312.123
CHROME_PATH = "C:\\Users\\phant\\IdeaProjects\\Chrome_Driver\\chromedriver"
DRIVER = webdriver.Chrome(options=chrome_options)

check_dict = {}     # 검색 여부 확인
snomed_dict = {}    # snomed 탐색한 리스트
parent_dict = {}    # 탐색이 끝났을 때 부모로 돌아갈 목적
rmdict = {}         # 삭제된 snomedct의 경우 종료일자 기록
queue = deque()     # 재귀 처리 목적의 deque


def open_snomed_file():
    # 기록된 snomed 값을 텍스트 파일에서 가져옴
    with open("./snomedct.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            # Code, Snomed명, 부모코드
            print(line)
            try:
                code, name, parent, rmdate = line.split(',')
                code = code.strip()
                name = name.strip()
                parent = parent.strip()
                rmdate = rmdate.strip()
                snomed_dict[code] = name    # 기록 가져오기 (추후 덮어쓰기용)
            except:
                code = line.split(',')[0]
                parent = line.split(',')[-2]

            check_dict[code] = True     # 탐색 여부 기록 (반복 탐색 방지)
            parent_dict[code] = parent
        print(code)
        # 가장 마지막에 기록된 코드를 queue의 시작으로 담음
        queue.append(code)

def dictionary_check():
    print(check_dict)
    print(snomed_dict)
    print(parent_dict)
    print(rmdict)


def open_page():
    URL = "https://www.findacode.com/snomed/"
    # # FIND-A-CODE 웹 페이지 열기
    DRIVER.get(URL)
    print(f"get URL : {URL}")

    try:
        # 웹 페이지에서 나타나는 모달 화면의 close 버튼 XPath 획득 후 닫기
        close_button = DRIVER.find_element(By.XPATH, '//*[@id="dailyMsgModal"]/div/div/div[3]/button')
        close_button.click()
        print("close button clicked")
    except:
        pass

def search_start():
    # 페이지의 검색 공간에 queue에 담긴 코드를 입력
    search_input = DRIVER.find_element(By.ID, "headerSearchStr3")
    search_input.send_keys(queue.pop())

    # 코드 검색 시도
    search_button = DRIVER.find_element(By.XPATH, '//*[@id="submit_search"]')
    search_button.click()

    # 검색 결과로 나오는 첫 번째 <a> 링크를 선택
    first_link = "#dataTable > tbody > tr > td > h4 > a"
    a_tag = DRIVER.find_element(By.CSS_SELECTOR, first_link)
    start_link = a_tag.get_attribute("href")

    surf_page(start_link)

def surf_page(link: str):
    # 검색 이후의 snomed 값 파도타기
    DRIVER.get(link)
    print(f"surf URL : {link}")


def find_snomed():
    target = DRIVER.find_element(By.XPATH, "//th[text()='SNOMED code']")
    code = target.find_element(By.XPATH, './following-sibling::td[1]').text
    print(f"find a code = {code}")

    return code

def find_codename():
    target = DRIVER.find_element(By.XPATH, "//th[text()='name']")
    codename = target.find_element(By.XPATH, './following-sibling::td[1]').text
    print(f"find a codename = {codename}")

    return codename

def find_parent():
    try:
        target = DRIVER.find_element(By.XPATH, "//td[text()='parents']")
        parent = target.find_element(By.XPATH, './following-sibling::td[1]/a').text
        print(f"find a parent = {parent}")
        return parent
    except:
        print("Not Found Parent..!")
        return "None"

def find_remove():
    target = DRIVER.find_element(By.XPATH, "//th[text()='status']")
    status = target.find_element(By.XPATH, './following-sibling::td[1]').text

    if status == 'removed':
        try:
            rmtarget = DRIVER.find_element(By.XPATH, "//th[text()='date removed']")
            rmdate = rmtarget.find_element(By.XPATH, './following-sibling::td[1]').text
            print(f"status 'removed' = {rmdate}")
            return rmdate
        except:
            rmdate = str(datetime.date.today())
            print(f"비활성 코드이지만 기록을 못참음 = {rmdate} 대체")
            return rmdate
    else:
        print(f"status is {status}")
        return "9999-12-31"

def find_children(parent_code):
    try:
        target = DRIVER.find_element(By.XPATH, "//td[text()='children']")

        children = target.find_elements(By.XPATH, './following-sibling::td[1]/ul/li')

        # elements에서 찾은 요소가 없으면 0이 된다  = 자식(children) 노드가 1개만 있다.
        if len(children) == 0:
            child = target.find_element(By.XPATH, "./following-sibling::td[1]")
            next_page = child.find_element(By.XPATH, "./a").get_attribute('href')
            queue.append(next_page)

            node = re.search(r'/(\d+)-', next_page)  # 링크 정보에서 snocd 추출
            parent_dict[node.group(1)] = parent_code

            print("queue에 적재 완료된 링크 리스트")
            print(f"1 : {next_page}")

        else:
            # 현재 페이지에 기록된 children 리스트를 queue에 담는다.
            print("queue에 적재 완료된 링크 리스트")
            for idx, child in enumerate(children):
                next_page = child.find_element(By.XPATH, './a').get_attribute('href')
                queue.append(next_page)

                # 부모 노드 정보를 parent_dict에 담는 과정
                node = re.search(r'/(\d+)-', next_page)  # 링크 정보에서 snocd 추출
                parent_dict[node.group(1)] = parent_code

                print(f"{idx+1} : {next_page}")

        print(f"queue에 적재된 링크 개수 = {len(queue)}")
    except:
        print("가장 마지막 자식 노드에 도착했습니다.")


def move_parent():
    target = DRIVER.find_element(By.XPATH, "//td[text()='parents']")
    parent = target.find_element(By.XPATH, './following-sibling::td[1]/a').get_attribute('href')
    queue.append(parent)


# 텍스트 파일 안에 snomed ct 값 적재
def write_code(code, name, parent, rmdate):
    #138875005, SNOMED CT Concept, None, 9999-12-31
    with open('./snomedct.txt', 'a', encoding='utf-8') as file:
        file.write('\n'+code + ', '+name+', '+parent+', '+rmdate)


if __name__ == '__main__':
    open_snomed_file()
    dictionary_check()
    open_page()
    search_start()
    fix_parent = parent_dict[find_snomed()] # 처음 탐색하는 노드의 부모
    start_node = find_snomed()
    find_children(start_node)                         # 시작하는 노드의 Children 적재

    """
    Queue에 있는 Children 노드 탐색
    이미 탐색했던 노드라면 넘김.
    Children을 다 순회하면 queue에 더 들어갈 노드가 없음
    --> 가장 처음 탐색했던 노드의 parent로 감.
    """
    while True:
        if not queue:  # queue에 더 이상 노드가 없다면
            if parent_dict[start_node] == 'None' : break
            else:
                # 부모 노드의 코드를 검색해 다시 탐색 시작
                open_page()
                queue.append(parent_dict[start_node])
                search_start()
                start_node = find_snomed()
                find_children(start_node)

        next_node = queue.pop()      # 다음 링크 노드
        surf_page(next_node)

        ncode = find_snomed()
        nname = find_codename()
        nparent = parent_dict[ncode]
        nrmdate = find_remove()

        # 최종 적재되지 않은 snomed code라면 적재 시작
        if ncode not in check_dict:
            check_dict[ncode] = True
            snomed_dict[ncode] = nname
            parent_dict[ncode] = nparent
            rmdict[ncode] = nrmdate

            print(f"적재할 노드 = {ncode}, {nname}, {nparent}, {nrmdate}")
            try:
                write_code(ncode, nname, nparent, nrmdate)
            except UnicodeEncodeError:
                pass

            find_children(ncode)    # children 노드를 찾으면서 dict에 상위 노드 정보 추가
            time.sleep(2)
        else:
            continue

