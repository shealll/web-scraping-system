import PySimpleGUI as sg
from datetime import date
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process
import pandas as pd
import webbrowser
import subprocess
import datetime
from webscraper import settings

from webscraper.spiders.Naturalspider import naturalspider
from webscraper.spiders.Politicspider import politicspider
from webscraper.spiders.Portspider import portspider

spiders = {
    "Natural Disaster": naturalspider,
    "Geopolitical Activity": politicspider,
    "Port News": portspider
}

day_scope = {
    "Recent 3 Months": 92,
    "Recent 6 Months": 183,
    "Recent 1 Year": 365,
    "Recent 2 Years": 730
}
sg.theme('LightBrown1')
BG_COLOR = 'Dark Blue'
F_COLOR = 'White'
COL_ITEM_SIZE = 22
#Radio buttons for Topic Modelling section
category_dict = {'Natural Disaster':'-R1-', 'Geopolitical Activity':'-R2-', 'Port News':'-R3-'}
samples_dict = {'Recent 1 year':'-R4-', 'Recent 2 years':'-R5-'}
 
# Main Menu
def make_window1():
    layout = [[sg.Text('Leveraging Web Scraping', justification='center', font='default 25',
                        text_color=F_COLOR, background_color=BG_COLOR, expand_x=True)],
              [sg.Text('in Predictive Modelling', justification='center', font='default 25',
                        text_color=F_COLOR, background_color=BG_COLOR, expand_x=True)],
              [sg.Text('of Supply Risk Detection', justification='center', font='default 25',
                       text_color=F_COLOR, background_color=BG_COLOR, expand_x=True)],
              [sg.Text("", size=(50,1), pad=(5,5))], 
              [sg.Text("In research of leveraging web scraping in predictive modelling of supply risk detection, a web scraping algorithm is developed to extract data regarding temporary events that cause supply risk. Then, the scraped output is tested using topic modelling for further analysis and examples of topic modelling visualizations are provided.", 
                        size=(60,5), justification='center', pad=(5,5), font='Helvetica 15')],
              [sg.Text("Note: This web scraping algorithm can only scrape up to the most recent two years. The web scraping duration may take around 45min to scrape a maximum of two years, depending on the internet connection.",
                        size=(60,3), justification='center', pad=(5,5), font='Helvetica 15')], 
              [sg.Text("", size=(50,1), pad=(5,5))], 
              [sg.Text('',size=(7,1)),
                sg.Button('Web Scraper',size=(12,1), enable_events=True, font='Helvetica 17'), 
               sg.Button('Topic Modelling',size=(15,1), enable_events=True, font='Helvetica 17'),
                 sg.Button('Exit',size=(10,1), enable_events=True, font='Helvetica 17')]]

    return sg.Window('Leveraging Web Scraping in Predictive Modelling of Supply Risk Detection', layout, finalize=True)

# Web Scraper
def make_window2():
    layout = [[sg.Text('Web Scraping Algorithm', justification='center', font='default 25',
                        text_color=F_COLOR, background_color=BG_COLOR, expand_x=True)],
            [sg.Text('For Temporary Events', justification='center', font='default 25',
                        text_color=F_COLOR, background_color=BG_COLOR, expand_x=True)],
            [sg.Text('that Cause Supply Risk', justification='center', font='default 25',
                        text_color=F_COLOR, background_color=BG_COLOR, expand_x=True)],                        
            [sg.Text()],
            [sg.Text('Choose A Temporary Event to scrape:', font='Helvetica 14')],
            [sg.Text('',size=(4,1)),
             sg.Combo(list(spiders.keys()), key='spider', background_color= 'white', text_color= 'black', font='Helvetica 14')],
            [sg.Text('Choose the time scope of the output:', font='Helvetica 14')],
            [sg.Text('',size=(10,1)),
             sg.Combo(list(day_scope.keys()), key='dayskey', background_color= 'white', text_color= 'black', font='Helvetica 14')],
            [sg.Text()],
            [sg.Text("The scraping process may take around (5 - 45) min.", size=(40,1), pad=(5,5), font='Helvetica 12')],
            [sg.Text('',size=(4,1)), sg.Button('Run' ,size=(10,1), enable_events=True, font='Helvetica 16'), 
            sg.Button('Exit',size=(10,1), enable_events=True, font='Helvetica 16')]]
    
    return sg.Window('Web Scraping Algorithm', layout, finalize=True)

# Topic Modelling
def make_window3():
    layout = [  [sg.Text('Topic Modelling Examples', justification='center', font='default 25', text_color=F_COLOR, background_color=BG_COLOR, expand_x=True)],
                [sg.Text("", size=(50,1), pad=(5,5))], 
                [ColumnParm('Temporary Event Category', 1, category_dict), ColumnParm('Samples', 2, samples_dict)],
                [sg.Button('Show Topic Model',size=(20,1),enable_events=True, key='-SHOWMODEL-', font='Helvetica 16')],
                [sg.Text("", size=(50,1), pad=(5,5))],
                [sg.Text('View Scraped Output Table:', justification='center', font='Helvetica 16')],
                [sg.Button('Load data',size=(10,1), enable_events=True, key='-LOADDATA-', font='Helvetica 16'), 
                sg.Button('Show data',size=(10,1),enable_events=True, key='-SHOWDATA-', font='Helvetica 16')],
                [sg.Text("", size=(30,1),key='-loaded-', pad=(5,5), font='Helvetica 14', background_color=F_COLOR)],
                [sg.Text("", size=(50,1), pad=(5,5))],
                [sg.Button('Back',size=(10,1), enable_events=True, font='Helvetica 16')]]
              
    return sg.Window('Leveraging Web Scraping in Predictive Modelling of Supply Risk Detection', layout, finalize=True)

# Column layout for topic modelling section
def ColumnParm(title, radio_group, radio_dict):
    layout = [[sg.Text(title,  size=(COL_ITEM_SIZE,1), justification='center', font='Current 16', text_color=F_COLOR, background_color=BG_COLOR)]]
    for item, key in radio_dict.items():
        layout += [[sg.Radio(item, group_id=radio_group, key=key, size=(COL_ITEM_SIZE,1), font='Current 13')]]
    return sg.Frame('',layout, )

def read_table():
    sg.set_options(auto_size_buttons=True)
    layout = [[sg.Text('Dataset (a CSV file)', size=(16, 1), font='Helvetica 11'),sg.InputText(),
               sg.FileBrowse(file_types=(("CSV Files", "*.csv"),("Text Files", "*.txt")),
                              initial_folder= r'webscraper\output')],
               [sg.Submit(), sg.Cancel()]]

    window1 = sg.Window('Input file', layout)
    try:
        event, values = window1.read()
        window1.close()
    except:
        window1.close()
        return
    
    filename = values[0]
    if filename == '':
        return

    data = []
    header_list = []

    if filename is not None:
        fn = filename.split('/')[-1]
        try:                     

            df = pd.read_csv(filename, sep=',', engine='python')
            # Uses the first row (which should be column names) as columns names
            header_list = list(df.columns)
            # Drops the first row in the table (otherwise the header names and the first row will be the same)
            data = df[1:].values.tolist()

            window1.close()
            return (df,data, header_list, fn)
        except:
            sg.popup_error('Error reading file')
            window1.close()
            return

def show_table(data, header_list, fn):    
    layout = [
        [sg.Table(values=data,
                  headings=header_list,
                  font='Helvetica',
                  pad=(25,25),
                  display_row_numbers=False,
                  auto_size_columns=True,
                  num_rows=min(25, len(data)))]
    ]

    window = sg.Window(fn, layout, grab_anywhere=False)
    event, values = window.read()
    window.close()

def show_ldavis(filename):
    # Read the contents of the HTML file

    # Open the HTML file in a web browser
    webbrowser.open(filename)

def reset_radio_buttons(window, radio_keys):
    for key in radio_keys:
        window[key].update(value=False)

# To create a process to run spiders         
def execute_crawling(spider_name, days_value):
    # Get the current date
    current_date = datetime.datetime.now().date()
    process = CrawlerProcess(get_project_settings())
    process.crawl(spiders[spider_name], current_date=current_date, days_year=days_value)
    process.start()
    process.join()

def main():
    # To end and restart the previous scraping process
    def restart_program():
        # Start a new instance of the program using subprocess
        subprocess.run(['python', 'Program.py'])
    read_successful = False
    window1, window2, window3 = make_window1(), None, None
    while True:
        window, event, values = sg.read_all_windows()
        if window == window1 and event in (sg.WIN_CLOSED, 'Exit'):
            break
        # Window 1 stuff
        if event == '-IN-':
            window['-OUTPUT-'].update(values['-IN-'])
        elif event == 'Web Scraper' and not window2:
            window2 = make_window2()
        #should make a global variable count instead
        elif event == 'Topic Modelling' and not window3:
            window3 = make_window3()

        # Window 2 stuff
        if window == window2 and event in(sg.WIN_CLOSED, 'Exit'):
            window2.close()
            window2 = None
        elif event == 'Run':
            spider_name = values['spider']
            if spider_name == '':
                sg.popup('Please select a temporary event!')
            elif values['dayskey'] != '':
                days_value = day_scope[values['dayskey']]
                try:
                    confirm_message = f"Do you want to scrape the temporary event \n- {spider_name}?"
                    if sg.popup_yes_no(confirm_message) == 'Yes':
                        p = Process(target=execute_crawling(spider_name, days_value))
                        p.start()
                        sg.popup(f"The data for {spider_name} has been extracted.")

                        window1.close()
                        window2.close()
                        restart_program()

                except ValueError:
                    sg.popup('The system did not manage to run that. Please re-enter the details!')

            else:
                sg.popup('Please select a time scope!')

        # Window 3 stuff
        if window == window3 and event in(sg.WIN_CLOSED, 'Back'):
            if window3 == None:
                break
            window3.close()
            read_successful=False
            window3 = None
        elif event == '-LOADDATA-':
            try:
                loaded_text = window['-loaded-']
                df,data, header_list, fn = read_table()
                read_successful = True
            except:
                pass
            if read_successful:
                loaded_text.update("Datset loaded: '{}'".format(fn))
            else:
                loaded_text.update("No dataset was loaded.")
        if event == '-SHOWDATA-':
            loaded_text = window['-loaded-']
            if read_successful:
                show_table(data,header_list,fn)
            else:
                loaded_text.update("No dataset was loaded.")
        if event == '-SHOWMODEL-':
            if values['-R4-'] == False and values['-R5-'] == False:
                sg.popup('Please select an option!')
            elif values['-R1-'] == False and values['-R2-'] == False and values['-R3-'] == False:
                sg.popup('Please select an option!')            
            elif values['-R1-'] == True and values['-R4-'] == True:
                show_ldavis(r'webscraper\LDA visualizations\naturaldisaster1y.html')
                reset_radio_buttons(window, ['-R1-', '-R4-'])        
            elif values['-R1-'] == True and values['-R5-'] == True:
                show_ldavis(r'webscraper\LDA visualizations\naturaldisaster2y.html')
                reset_radio_buttons(window, ['-R1-', '-R5-']) 
            elif values['-R2-'] == True and values['-R4-'] == True:
                show_ldavis(r'webscraper\LDA visualizations\geopolitics1y.html')
                reset_radio_buttons(window, ['-R2-', '-R4-'])         
            elif values['-R2-'] == True and values['-R5-'] == True:
                show_ldavis(r'webscraper\LDA visualizations\geopolitics2y.html')
                reset_radio_buttons(window, ['-R2-', '-R5-'])             
            elif values['-R3-'] == True and values['-R4-'] == True:
                show_ldavis(r'webscraper\LDA visualizations\portnews1y.html')         
                reset_radio_buttons(window, ['-R3-', '-R4-'])
            elif values['-R3-'] == True and values['-R5-'] == True:
                show_ldavis(r'webscraper\LDA visualizations\portnews2y.html') 
                reset_radio_buttons(window, ['-R3-', '-R5-'])
    
    if window2 is not None:
        window2.close()
    if window3 is not None:
        window3.close()

if __name__ == '__main__':
    main()