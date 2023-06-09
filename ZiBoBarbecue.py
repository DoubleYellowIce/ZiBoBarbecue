from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, time
from time import sleep
import schedule

phone_num = "13129185168"
reserve_time = '12:00'
cnt_of_tabs = 10
script_start_time = '11:59'


def routine(chrome):
    chrome.get("https://yy.bcwhkj.cn/h5/y.html?vs=12")
    phone_num_input = WebDriverWait(chrome, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "yinying-auto"))
    )
    phone_num_input.clear()
    phone_num_input.send_keys(phone_num)
    select_table_drop_down = Select(WebDriverWait(chrome, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[1]/div[5]/select'))
    ))
    select_table_drop_down.select_by_index(1)


def reserve_repeatedly():
    options = Options()
    options.add_experimental_option("detach", True)
    chrome = webdriver.Chrome(options=options)
    for i in range(1, cnt_of_tabs + 1):
        routine(chrome)
        if i != cnt_of_tabs:
            chrome.switch_to.new_window('tab')
    wait_for_specific_time()
    current_try_time = 1
    for current_tab in reversed(chrome.window_handles):
        if current_try_time != 1:
            chrome.switch_to.window(current_tab)
        try:
            reserve_btn = WebDriverWait(chrome, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[1]/div[7]/a'))
            )
            reserve_btn.click()
        except TimeoutException:
            print("第" + str(current_try_time) + "次等待预约按钮出现超时")
        finally:
            print('第' + str(current_try_time) + '次尝试预约。')
            current_try_time += 1

    current_try_time = 1
    for current_tab in reversed(chrome.window_handles):
        chrome.switch_to.window(current_tab)
        if current_try_time != 1:
            chrome.switch_to.window(current_tab)
        reserve_result = ''
        try:
            # TODO
            # 应该还要判断是否预约成功了
            reserve_result = WebDriverWait(chrome, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="layui-layer4"]/div[2]'))
            ).text
            print("第" + str(current_try_time) + "次预约结果为" + reserve_result)
        except TimeoutException:
            # TODO 🌟🌟🌟
            # 应该自动截屏并保存在相应的日期文件夹里。
            print("第" + str(current_try_time) + "次等待预约结果超时")
        finally:
            current_try_time += 1
            if reserve_result == '预约失败，当前场次没有空位了' or reserve_result == '未到可预定时段':
                chrome.close()


def wait_for_specific_time():
    start_time = time(*(map(int, reserve_time.split(':'))))
    sleep_times = 1
    while start_time > datetime.today().time():  # you can add here any additional variable to break loop if necessary
        print('未到开抢时间，第' + str(sleep_times) + '次休眠。')
        sleep_times += 1
        sleep(0.05)  # you can change 0.1 sec interval to any other
    print('休眠结束，开始抢号。')


schedule.every().day.at(script_start_time).do(reserve_repeatedly)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        sleep(1)
