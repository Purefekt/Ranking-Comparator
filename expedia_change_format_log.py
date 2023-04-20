import os
import undetected_chromedriver as uc
from const import CHROME_VERSION
import time
from selenium.webdriver.common.by import By
import gzip


def determine_rating_type(html_file_path):

    opts = uc.ChromeOptions()
    opts.headless = True
    opts.add_argument('--headless')
    driver = uc.Chrome(version_main=CHROME_VERSION, suppress_welcome=False, options=opts)
    url_file_path = 'file://' + html_file_path
    driver.get(url_file_path)

    time.sleep(1)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    all_listings_element = driver.find_elements(By.CSS_SELECTOR, 'div[data-stid="property-listing-results"]')[0]
    all_listings = all_listings_element.find_elements(By.CSS_SELECTOR, 'div.uitk-spacing.uitk-spacing-margin-blockstart-three')

    flag_out_of_10 = False
    flag_divided_by_10 = False
    flag_out_of_5 = False
    flag_divided_by_5 = False

    for i in range(len(all_listings)):
        if 'out of 10' in all_listings[i].text:
            flag_out_of_10 = True
        if '/10' in all_listings[i].text:
            flag_divided_by_10 = True
        if 'out of 5' in all_listings[i].text:
            flag_out_of_5 = True
        if '/5' in all_listings[i].text:
            flag_divided_by_5 = True

        if (flag_divided_by_10 is True and flag_out_of_10 is True) or (flag_divided_by_5 is True or flag_out_of_5 is True):
            break

    if flag_divided_by_10 is True and flag_out_of_10 is True:
        return '10'
    elif flag_divided_by_5 is True and flag_out_of_5 is True:
        return '5'
    else:
        return 'None'

dir_path = "/Users/dproserp/Desktop/raw_data_remote/search"
output_path = "/Users/dproserp/Desktop/raw_data_remote/log/"
files = os.listdir(dir_path)

for filename in files:
    if filename != '.DS_Store':
        # write a new csv for each folder
        fhand = open(output_path + filename + '.csv', 'w')
        fhand.writelines('city,search start and end date,type of rating\n')
        run_date_dir = dir_path + '/' + filename
        for city_file in os.listdir(run_date_dir):
            if city_file != '.DS_Store':
                print(f'On city {city_file}')
                city_dir = run_date_dir + '/' + city_file
                for search_start_end_date in os.listdir(city_dir):
                    if search_start_end_date != '.DS_Store':
                        page_html_zip_file_path = city_dir + '/' + search_start_end_date + '/page.html.gz'
                        html_file_name = city_dir + '/' + search_start_end_date + '/page.html'

                        with gzip.open(page_html_zip_file_path, 'rb') as f_in:
                            with open(html_file_name, 'wb') as f_out:
                                f_out.write(f_in.read())

                                # process it
                                city_name = city_file.split(',')[0]
                                print(f'On date {search_start_end_date}')
                                print(html_file_name)
                                try:
                                    rating_version = determine_rating_type(html_file_name)
                                except:
                                    rating_version = 'error in html page'
                                fhand.writelines(city_name + ',' + search_start_end_date + ',' + rating_version + '\n')
                                os.remove(html_file_name)
        fhand.close()
