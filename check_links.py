# -*- coding: utf-8 -*-
import re

for filename in ['alipansou_result.html', 'upyunso_result.html']:
    print(f'\n=== {filename} ===')
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找各种网盘链接
    aliyun = re.findall(r'aliyundrive\.com/s/[a-zA-Z0-9]+', content)
    quark = re.findall(r'pan\.quark\.cn/s/[a-zA-Z0-9]+', content)
    baidu = re.findall(r'pan\.baidu\.com/s/[a-zA-Z0-9]+', content)
    
    # 查找href中的链接
    hrefs = re.findall(r'href=["\']([^"\']*(?:aliyun|quark|baidu)[^"\']*)["\']', content, re.I)
    
    print(f'Aliyun links: {len(aliyun)}')
    print(f'Quark links: {len(quark)}')
    print(f'Baidu links: {len(baidu)}')
    print(f'Hrefs with pan: {hrefs[:5]}')
    
    # 查找data属性中的链接
    data_links = re.findall(r'data-[^=]*=["\']([^"\']+)["\']', content)
    for link in data_links[:10]:
        if 'http' in link:
            print(f'Data link: {link}')

