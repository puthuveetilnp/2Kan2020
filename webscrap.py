import bs4 as bs
import urllib.request
import pickle
import pandas as pd




def get_text(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    source = urllib.request.urlopen(req).read()
    # source = urllib.request.urlopen(home_page).read()
    soup = bs.BeautifulSoup(source, 'lxml')

    string_website = ""
    # print(soup.find_all('p'))
    for paragraph in soup.find_all('p'):
        string_website = ' '.join([string_website, str(paragraph.text)])
# print(string_website)

    url_list = list()
    for link in soup.find_all('a'):
        url_str = link.get('href')
        if (url in url_str):
            url_list.append(url_str)
    if(len(url_list) > 7):
        url_list=url_list[1:7]
        print(url_list)
    print(len(url_list))
    for web_link in url_list:
        if ('location' not in url):
            sub_req = urllib.request.Request(web_link, headers={'User-Agent': 'Mozilla/5.0'})
            sub_source = urllib.request.urlopen(sub_req).read()
            # source = urllib.request.urlopen(home_page).read()
            sub_page = bs.BeautifulSoup(sub_source, 'lxml')
            for paragraph in sub_page.find_all('p'):
                string_website = ' '.join([string_website, str(paragraph.text)])
    return string_website



def main():
    with open('/Users/awong234/PycharmProjects/technica2020/real_urls.p', 'rb') as f:
        real_url = pickle.load(f)
    real_url = [s.rstrip() for s in real_url]
    print(real_url)
    with open('/Users/awong234/PycharmProjects/technica2020/fake_urls.p', 'rb') as f:
        fake_url = pickle.load(f)
    fake_url = [s.rstrip() for s in fake_url]
    fake_url = fake_url[1:201]
    with open('fake_url.pkl', 'wb') as fh:
        pickle.dump(fake_url, fh)

    print(len(fake_url))

    real_data_list=list()
    for url in real_url:
        try:
            paragraph=get_text(url)
            if paragraph !='':
                real_data=(paragraph,"real")
        except:
            pass
        real_data_list.append(real_data)

    fake_data_list = list()
    for url in fake_url:
        try:
            paragraph = get_text(url)
            if paragraph != '':
                fake_data = (paragraph, "real")
        except:
            pass
        fake_data_list.append(fake_data)



    with open('real_data_training.pkl', 'wb') as f:
        pickle.dump(real_data_list, f)

    with open('fake_data_training.pkl', 'wb') as fh:
        pickle.dump(fake_data_list, fh)
if __name__=="__main__":
    main()