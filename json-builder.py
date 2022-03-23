from pathlib import Path
import sys
import subprocess
import json

def get_pdf_page_number(book):
    pdfinfo = subprocess.Popen(['pdfinfo',str(book)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    grep = subprocess.run(['grep','-a','Pages'],stdin=pdfinfo.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8')

    stdout = grep.stdout
    return int(stdout.replace(' ','').split(':')[1])

def get_full_work_title(artist, book_title, title):
    return "{}/{}/{}".format(artist, book_title, title)

def construct_work_id_map(work_list):
    workToId = {}
    idToWork = {}

    for work in work_list:
        full_work_title = get_full_work_title(work['artist'], work['book_title'], work['title'])

        workToId[full_work_title] = work['id']
        idToWork[work['id']] = full_work_title

    return workToId,idToWork

args = sys.argv

# ベースパスは artist/book.pdf という２層になっていることを想定
base_dir_path = Path(args[1])

if base_dir_path.exists() is False:
    print(str(base_dir_path) + 'is not exist')
    exit(1)


input_work_list = []
if len(args) >= 3:
    input_json_path = Path(args[2])

    if input_json_path.exists():
        with open(input_json_path, 'r') as f:
            input_work_list = json.load(f)

input_work_to_id, input_id_to_work = construct_work_id_map(input_work_list)


artist_dir_list = [x for x in base_dir_path.iterdir() if x.is_dir()]

work_id = 0
work_list = []

for artist_dir in artist_dir_list:
    artist_name = artist_dir.name

    for book in artist_dir.iterdir():
        if book.suffix == '.pdf':
            book_title = book.stem

            bookmarks = subprocess.run(['jpdfbookmarks','--dump',str(book)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,encoding='utf-8').stdout

            book_page_number = get_pdf_page_number(book)

            work_list_of_book = []
            for line in bookmarks.splitlines():
                work_title = line.split(',')[0].split('/')[0]
                work_start_page_number = line.split(',')[0].split('/')[1]

                work = {}
                work['artist'] = artist_name
                work['book_title'] = book_title
                work['title'] = work_title
                work['startPageNumber'] = int(work_start_page_number)

                work_list_of_book.append(work)
            
            # 作品の終了ページは次の作品の開始ページの直前とする
            for i,work in enumerate(work_list_of_book):
                work['id'] = work_id
                work_id = work_id + 1

                if i is not (len(work_list_of_book) - 1):
                    work['endPageNumber'] = work_list_of_book[i+1]['startPageNumber'] - 1
                else:
                    work['endPageNumber'] = book_page_number

                work_list.append(work)


work_to_id, id_to_work = construct_work_id_map(work_list)

for work in work_list:
    full_work_title = get_full_work_title(work['artist'], work['book_title'], work['title'])
    id_in_input = input_work_to_id.get(full_work_title, -1)

    prev_work_id = -1
    next_work_id = -1
    # 入力されたリストに作品情報があった時にはシリーズ物の情報を更新する必要がある
    if id_in_input != -1:
        # input_work_listがidでソートされていることを前提にしている
        work_in_input = input_work_list[id_in_input]

        if 'prevWorkId' in work_in_input:
            prev_full_work_title = input_id_to_work.get(work_in_input['prevWorkId'],"")

            prev_work_id = work_to_id.get(prev_full_work_title,-1)

        if 'nextWorkId' in work_in_input:
            next_full_work_title = input_id_to_work.get(work_in_input['nextWorkId'],"")

            next_work_id = work_to_id.get(next_full_work_title,-1)

    work['prevWorkId'] = prev_work_id
    work['nextWorkId'] = next_work_id

print(json.dumps(work_list,indent=2,ensure_ascii=False))
