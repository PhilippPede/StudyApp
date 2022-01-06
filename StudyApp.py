import tkinter as tk
import random
import datetime as dt

from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np

# sources
#    basic intro: https://realpython.com/python-gui-tkinter/
#    https://zetcode.com/tkinter/layout/
#    https://stackoverflow.com/questions/34276663/tkinter-gui-layout-using-frames-and-grid
#    wrap things up in a class: https://stackoverflow.com/questions/8959815/restricting-the-value-in-tkinter-entry-widget
#
#    tkinter colorChart: http://www.science.smith.edu/dftwiki/images/3/3d/TkInterColorCharts.png

#########################################################################################
#     initialize variables
#########################################################################################
list_deckToPractice = []

nCardsPracticed = 0
nCardsInDeck    = 10 # default value

filename_dictionary  = "dictionary.csv"
filename_studyLog    = "studyLog.csv"
filename_studyStatus = "studyStatus.csv"
# [TESTING] filename_studyLog    = "studyLog_TESTING.csv"
# [TESTING] filename_studyStatus = "studyStatus_TESTING.csv"

# relative weight of features that contribute to overall urgency-score of a card
weight_nDaysLastSeen    = 1.00 # how recent the card was seen
weight_repetitionNumber = 1.00 # how often card was correct most recently
weight_fractionCorrect  = 0.75 # how often cared was correct overall
weight_currentRating    = 0.50 # how the card is currently ranked
weight_randomNoise      = 0.50 # random noise
weight_ratingChange     = 0.25 # most recent change

list_ratings_correct = [4,5,6]
list_ratings_wrong   = [1,2,3]
list_ratings_bad     = [1,2]
list_ratings_medium  = [3,4]
list_ratings_good    = [5,6]

#########################################################################################
#     read files
#########################################################################################
df_dictionary = pd.read_csv(filename_dictionary, index_col=0)
df_studyStatus = pd.read_csv(filename_studyStatus, index_col=[0,1])

#########################################################################################    
#     function: shuffle_deck()
#########################################################################################
def shuffle_deck(list_deckToPractice):
    random.shuffle(list_deckToPractice)

#########################################################################################
#     function: parse_cardInfo()
#########################################################################################
def parse_cardInfo(dict_card):
    # if mode is already set, don't recalculate it
    if "mode" not in dict_card:
        raise NotImplementedError("Mode was not set when parsing card with id {}".format(id))

    if dict_card["mode"] == "cn2en":
        str_cardFront = dict_card["cn"]
        str_cardBack  = dict_card["cn"] + "\n\n\n" + dict_card["py"] + "\n\n" + dict_card["en"]
    elif dict_card["mode"] == "en2cn":
        str_cardFront = dict_card["en"]
        str_cardBack = dict_card["en"] + "\n\n\n" + dict_card["cn"] + "\n\n" + dict_card["py"]
    else:
        raise NotImplementedError("Unknown mode {}".format(dict_card["mode"]))

    return str_cardFront, str_cardBack

#########################################################################################
#     function: display_card()
#########################################################################################
def display_card(text):
    lbl_card["text"] = text

#########################################################################################
#     function: enable_buttonsClassify()
#########################################################################################
def enable_buttonsClassify():
    for btn_classify in list_btn_classify:
        btn_classify["state"] = "normal"

#########################################################################################
#     function: disable_buttonsClassify()
#########################################################################################
def disable_buttonsClassify():
    for btn_classify in list_btn_classify:
        btn_classify["state"] = "disable"

#########################################################################################
#     function: disable_buttonsFlip()
#########################################################################################
def disable_buttonFlip():
    btn_flip["state"] = "disable"

#########################################################################################
#     function: enable_buttonFlip()
#########################################################################################
def enable_buttonFlip():
    btn_flip["state"] = "normal"

#########################################################################################
#     function: disable_settings()
#########################################################################################
def disable_settings():
    ent_nCardsToStudy["state"] = "disable"
    rdb_cn2en["state"] = "disable"
    rdb_en2cn["state"] = "disable"
    rdb_both["state"] = "disable"
    rdb_newCards["state"] = "disable"
    rdb_allCards["state"] = "disable"
    rdb_goodCards["state"] = "disable"
    rdb_mediumCards["state"] = "disable"
    rdb_badCards["state"] = "disable"
    btn_start["state"] = "disable"

#########################################################################################
#     function: enable_settings()
#########################################################################################
def enable_settings():
    ent_nCardsToStudy["state"] = "normal"
    rdb_cn2en["state"] = "normal"
    rdb_en2cn["state"] = "normal"
    rdb_both["state"] = "normal"
    rdb_newCards["state"] = "normal"
    rdb_allCards["state"] = "normal"
    rdb_goodCards["state"] = "normal"
    rdb_mediumCards["state"] = "normal"
    rdb_badCards["state"] = "normal"
    btn_start["state"] = "normal"

#########################################################################################
#     function: flip_card()
#########################################################################################
def flip_card():
    _, str_cardBack = parse_cardInfo(list_deckToPractice[nCardsPracticed])
    display_card(text=str_cardBack)
    enable_buttonsClassify()

#########################################################################################
#     function: flip_card()
#########################################################################################
def keyshortcut_space(event):
    # note that key-shortcuts need the event argument
    # only flip if button is active (bound to <space>)
    if btn_flip["state"] != "disabled":
        _, str_cardBack = parse_cardInfo(list_deckToPractice[nCardsPracticed])
        display_card(text=str_cardBack)
        enable_buttonsClassify()

#########################################################################################
#     function: update_studyStatusFile()
#########################################################################################
def update_studyStatusFile():
    # ----- add new card
    for dict_card in list_deckToPractice:
        key = (dict_card["id"],dict_card["mode"])
        if key not in df_studyStatus.index:
            str_firstReviewDate = dict_card["date"]
            str_lastReviewDate = dict_card["date"]
            rating = dict_card["rating"]
            previousRating = dict_card["rating"]
            repetitionNumber = 1 if rating in list_ratings_correct else 0
            nTimesSeen = 1
            nTimesCorrect = 1 if rating in list_ratings_correct else 0
            nTimesWrong = 1 if rating in list_ratings_wrong else 0
            nTimesBad = 1 if rating in list_ratings_bad else 0
            nTimesMedium = 1 if rating in list_ratings_medium else 0
            nTimesGood = 1 if rating in list_ratings_good else 0

            df_studyStatus.loc[key,:]=[str_firstReviewDate,
                                       str_lastReviewDate,
                                       rating,
                                       previousRating,
                                       repetitionNumber,
                                       nTimesSeen,
                                       nTimesCorrect,
                                       nTimesWrong,
                                       nTimesBad,
                                       nTimesMedium,
                                       nTimesGood]

        # ----- update existing card
        else:
            str_firstReviewDate = df_studyStatus.loc[key,"firstReviewDate"]
            str_lastReviewDate = dict_card["date"]
            rating = dict_card["rating"]
            previousRating = df_studyStatus.loc[key,"rating"]
            repetitionNumber = df_studyStatus.loc[key,"repetitionNumber"]+1 if rating in list_ratings_correct else 0
            nTimesSeen = df_studyStatus.loc[key, "nTimesSeen"]+1
            nTimesCorrect = df_studyStatus.loc[key, "nTimesCorrect"]+1 if rating in list_ratings_correct else \
                            df_studyStatus.loc[key, "nTimesCorrect"]
            nTimesWrong = df_studyStatus.loc[key, "nTimesWrong"]+1 if rating in list_ratings_wrong else \
                          df_studyStatus.loc[key, "nTimesWrong"]
            nTimesBad = df_studyStatus.loc[key, "nTimesBad"]+1 if rating in list_ratings_bad else \
                        df_studyStatus.loc[key, "nTimesBad"]
            nTimesMedium = df_studyStatus.loc[key, "nTimesMedium"]+1 if rating in list_ratings_medium else \
                           df_studyStatus.loc[key, "nTimesMedium"]
            nTimesGood = df_studyStatus.loc[key, "nTimesGood"]+1 if rating in list_ratings_good else \
                         df_studyStatus.loc[key, "nTimesGood"]

            df_studyStatus.loc[key, :] = [str_firstReviewDate,
                                          str_lastReviewDate,
                                          rating,
                                          previousRating,
                                          repetitionNumber,
                                          nTimesSeen,
                                          nTimesCorrect,
                                          nTimesWrong,
                                          nTimesBad,
                                          nTimesMedium,
                                          nTimesGood]

    df_studyStatus.to_csv(filename_studyStatus, mode='w', header=True, index=True)


#########################################################################################
#     function: show_summary()
#########################################################################################
def show_summary():
    df = pd.DataFrame(list_deckToPractice)
    df = df[["id", "date", "time", "mode", "rating"]]
    lbl_card["text"] = "Finished, Well Done!"
    lbl_card["text"] += "\n\nResults\n"

    df_valCounts_num = df['rating'].value_counts()
    df_valCounts_perc = df['rating'].value_counts(normalize=True)

    for rating in [1, 2, 3, 4, 5, 6]:
        if rating not in df_valCounts_num:
            valCounts_num = 0
            valCounts_perc = 0
        else:
            valCounts_num = df_valCounts_num[rating]
            valCounts_perc = df_valCounts_perc[rating]
        lbl_card["text"] += "[Rating = {}] ... {:3d} ({:5.1f}%)\n".format(rating, valCounts_num, valCounts_perc * 100)

#########################################################################################
#     function: update_studyLogFile()
#########################################################################################
def update_studyLogFile():
    df = pd.DataFrame(list_deckToPractice)
    df = df[["id", "date", "time", "mode", "rating"]]
    df.to_csv(filename_studyLog, mode='a', header=False, index=False)

#########################################################################################
#     function: log_results()
#########################################################################################
def log_results():
    # ----- update studyStatus
    update_studyStatusFile()

    # ----- update studyLog
    update_studyLogFile()

    # ----- display summary stats
    show_summary()

    # ----- update vocabulary breakdown
    display_ratingBreakdown()


#########################################################################################
#     function: assign_value_1()
#########################################################################################
def log_cardOutcome():
    global nCardsPracticed

    dt_now = dt.datetime.now()
    list_deckToPractice[nCardsPracticed]["date"] = dt_now.strftime("%Y/%m/%d")
    list_deckToPractice[nCardsPracticed]["time"] = dt_now.strftime("%H:%M:%S")

    # if session finished: summarize the results
    if nCardsPracticed == len(list_deckToPractice) - 1:
        disable_buttonsClassify()
        disable_buttonFlip()
        enable_settings()
        log_results()
    else:
        # get next card
        nCardsPracticed += 1
        update_lbl_progress()

        # prepare next card
        str_cardFront, str_cardBack = parse_cardInfo(list_deckToPractice[nCardsPracticed])
        display_card(text=str_cardFront)
        disable_buttonsClassify()

#########################################################################################    
#     function: assign_value_1()
#########################################################################################
def assign_value_1():
    list_deckToPractice[nCardsPracticed]["rating"] = 1
    log_cardOutcome()

#########################################################################################    
#     function: assign_value_2()
#########################################################################################
def assign_value_2():
    list_deckToPractice[nCardsPracticed]["rating"] = 2
    log_cardOutcome()
    
#########################################################################################    
#     function: assign_value_3()
#########################################################################################
def assign_value_3():
    list_deckToPractice[nCardsPracticed]["rating"] = 3
    log_cardOutcome()

#########################################################################################
#     function: assign_value_3()
#########################################################################################
def assign_value_4():
    list_deckToPractice[nCardsPracticed]["rating"] = 4
    log_cardOutcome()

#########################################################################################
#     function: assign_value_5()
#########################################################################################
def assign_value_5():
    list_deckToPractice[nCardsPracticed]["rating"] = 5
    log_cardOutcome()

#########################################################################################
#     function: assign_value_6()
#########################################################################################
def assign_value_6():
    list_deckToPractice[nCardsPracticed]["rating"] = 6
    log_cardOutcome()
 
#########################################################################################    
#     function: update_lbl_progress()
#########################################################################################
def update_lbl_progress():
    lbl_progress["text"] = "{} / {}".format(nCardsPracticed+1, len(list_deckToPractice))

#########################################################################################
#     function: createDeck_fromDictionary()
#########################################################################################
def createDeck_fromDictionary(list_ids, mode):
    if mode not in ["en2cn", "cn2en"]:
        raise ValueError("Unknown practice mode {}".format(mode))

    list_deckToPractice=[]
    for id in list_ids:
        dictionary_entry = df_dictionary.loc[id]
        newCard = {}
        newCard["cn"] = dictionary_entry["Chinese"]
        newCard["py"] = dictionary_entry["PinYin"]
        newCard["en"] = dictionary_entry["English"]
        newCard["id"] = id
        newCard["mode"] = mode
        list_deckToPractice.append(newCard)
    return list_deckToPractice

#########################################################################################
#     function: createDeck_NewCards()
#########################################################################################
def createDeck_NewCards():
    nCardsToStudy = int(ent_nCardsToStudy.get())

    list_idOfNewCards = sorted(list(set(df_dictionary.index) - set(df_studyStatus.index.levels[0])))
    list_idOfSelectedCards = list_idOfNewCards[:nCardsToStudy]

    # when we get new cards, store them in both directions
    list_deckToPractice1 = createDeck_fromDictionary(list_ids=list_idOfSelectedCards, mode="cn2en")
    list_deckToPractice2 = createDeck_fromDictionary(list_ids=list_idOfSelectedCards, mode="en2cn")

    return list_deckToPractice1+list_deckToPractice2

#########################################################################################
#     function: add_featuresForScoring()
#########################################################################################
def add_featuresForScoring(df):
    # engineer such that higher value ==> more urgent

    # time-urgency - based on how recent the card was last seen
    #   ==> the longer ago that was, the more urgent the card
    df["feat_dtToday"] = pd.to_datetime(dt.date.today())
    df["feat_dtLastReviewDate"] = pd.to_datetime(df["lastReviewDate"], format="%Y/%m/%d")
    df["feat_nDaysLastSeen"] = (df["feat_dtToday"] - df["feat_dtLastReviewDate"]).dt.days

    # trend-urgency - based on whether the card is getting better or worse
    #   ==> if card got much worse, it is higher priority
    df["feat_ratingChange"] = -(df["rating"] - df["previousRating"])

    # repetition-urgency - based on how often in a row the card was remembered correctly
    #   ==> the fewer times the card was recalled correctly, the more urgent
    df["feat_repetitionNumber"] = -df["repetitionNumber"]

    # difficulty-urgency - based on fraction of how often card was correct
    #   ==> the fewer times the card was recalled correctly, the more urgent
    df["feat_fractionCorrect"] = -(df["nTimesCorrect"] / df["nTimesSeen"])

    # random-noise - based on uniform(0,1)
    df["feat_randomNoise"] = np.random.uniform(0, 1, df.shape[0])

#########################################################################################
#     function: add_urgencyScore()
#########################################################################################
def add_urgencyScore(df):
    if df.shape[0] <= int(ent_nCardsToStudy.get()):
        df["score"] = 1.0
    else:
        min_max_scaler=MinMaxScaler()
        df[["score_nDaysLastSeen",
            "score_repetitionNumber",
            "score_fractionCorrect",
            "score_currentRating",
            "score_ratingChange"]] = \
            min_max_scaler.fit_transform(df[["feat_nDaysLastSeen",
                                             "feat_repetitionNumber",
                                             "feat_fractionCorrect",
                                             "rating",
                                             "feat_ratingChange"]])

        df["score"] = weight_nDaysLastSeen * df["score_nDaysLastSeen"]        + \
                      weight_repetitionNumber * df["score_repetitionNumber"]  + \
                      weight_fractionCorrect * df["score_fractionCorrect"]    + \
                      weight_currentRating * df["score_currentRating"]        + \
                      weight_randomNoise * df["feat_randomNoise"]             + \
                      weight_ratingChange * df["score_ratingChange"]

#########################################################################################
#     function: createDeck_SelectByRating()
#########################################################################################
def createDeck_SelectByRating(list_ratings):
    nCardsToStudy = int(ent_nCardsToStudy.get())

    # ----- select universe of cards that could be practiced
    if mode_study.get() == MODE_STUDY_CN2EN:
        df_select = df_studyStatus.loc[pd.IndexSlice[:, "cn2en"],]
    elif mode_study.get() == MODE_STUDY_EN2CN:
        df_select = df_studyStatus.loc[pd.IndexSlice[:, "en2cn"],]
    elif mode_study.get() == MODE_STUDY_BOTH:
        df_select = df_studyStatus.loc[pd.IndexSlice[:, ["en2cn","cn2en"]],]

    df_select = df_select[df_select["rating"].isin(list_ratings)].copy(deep=True)

    # if no cards there to practice
    if df_select.shape[0] == 0:
        return []

    # compute features & ranking
    add_featuresForScoring(df_select)
    add_urgencyScore(df_select)
    df_select.sort_values(by="score", ascending=False, inplace=True)

    list_deckToPractice=[]
    for i_newCard in range(nCardsToStudy):
        if i_newCard >= df_select.shape[0]:
            break
        id_newCard, mode_newCard = df_select.iloc[i_newCard].name
        list_deckToPractice += createDeck_fromDictionary(list_ids=[id_newCard], mode=mode_newCard)

    return list_deckToPractice

#########################################################################################
#     function: start_practice()
#########################################################################################
def start_practice():
    global nCardsPracticed
    global list_deckToPractice

    if mode_cardSelection.get() == MODE_CARDSELECT_NEW:
        list_deckToPractice = createDeck_NewCards()
    elif mode_cardSelection.get() == MODE_CARDSELECT_ALL:
        list_deckToPractice = createDeck_SelectByRating(list_ratings=[1,2,3,4,5,6])
    elif mode_cardSelection.get() == MODE_CARDSELECT_GOOD:
        list_deckToPractice = createDeck_SelectByRating(list_ratings=[5,6])
    elif mode_cardSelection.get() == MODE_CARDSELECT_BAD:
        list_deckToPractice = createDeck_SelectByRating(list_ratings=[1,2])
    elif mode_cardSelection.get() == MODE_CARDSELECT_MEDIUM:
        list_deckToPractice = createDeck_SelectByRating(list_ratings=[3,4])
    elif mode_cardSelection.get() == MODE_CARDSELECT_RATING:
        list_deckToPractice = createDeck_SelectByRating(list_ratings=[ratingSelect.get()])
    else:
        raise NotImplementedError

    if len(list_deckToPractice) > 0:
        disable_settings()
        enable_buttonFlip()
        ent_nCardsToStudy.insert(tk.END, str(len(list_deckToPractice)))

        shuffle_deck(list_deckToPractice)
        nCardsPracticed = 0

        update_lbl_progress()

        str_cardFront, _ = parse_cardInfo(list_deckToPractice[nCardsPracticed])
        display_card(text=str_cardFront)
        disable_buttonsClassify()
    else:
        lbl_card["text"] = "No cards found that match the criteria...\n\nPlease select again"

#########################################################################################
#     function: display_ratingBreakdown()
#########################################################################################
def display_ratingBreakdown():
    list_ratings = [1,2,3,4,5,6]
    df_en2cn = df_studyStatus.loc[pd.IndexSlice[:, "en2cn"],]
    df_cn2en = df_studyStatus.loc[pd.IndexSlice[:, "cn2en"],]
    nTotal_en2cn = df_en2cn.shape[0]
    nTotal_cn2en = df_cn2en.shape[0]

    if nTotal_en2cn != nTotal_cn2en:
        raise ValueError("Unsymmetric breakdown of total cards into en2cn ({}) and cn2en ({})".format(nTotal_en2cn,
                                                                                                      nTotal_cn2en))
    for i, rating in enumerate(list_ratings):
        nRating_val_en2cn = df_en2cn[df_en2cn["rating"] == rating].shape[0]
        nRating_val_cn2en = df_cn2en[df_cn2en["rating"] == rating].shape[0]
        if nTotal_en2cn > 0:
            nRating_perc_en2cn = nRating_val_en2cn/nTotal_en2cn
            nRating_perc_cn2en = nRating_val_cn2en/nTotal_cn2en
        else:
            nRating_perc_en2cn = 0.0
            nRating_perc_cn2en = 0.0
        list_lbl_valRatings[i]["text"] = "{:4d} ({:4.0f}%) | {:4d} ({:4.0f}%)".format(nRating_val_en2cn,
                                                                                      nRating_perc_en2cn * 100,
                                                                                      nRating_val_cn2en,
                                                                                      nRating_perc_cn2en * 100)
    lbl_valTotal["text"] = "{:4d}".format(nTotal_en2cn)

    # get new cards
    list_idOfNewCards = sorted(list(set(df_dictionary.index) - set(df_studyStatus.index.levels[0])))
    lbl_valNew["text"] = "{:4d}".format(len(list_idOfNewCards))

#########################################################################################    
#     set up the GUI framework
#########################################################################################   
window = tk.Tk()
window.title("My Study App")

window.rowconfigure(0, minsize=400, weight=1)
window.columnconfigure(0, minsize=150, weight=1)
window.columnconfigure(1, minsize=500, weight=1)
window.columnconfigure(2, minsize=150, weight=1)

# ----- frame for settings
fr_settings = tk.Frame(window, width=150, bg="grey22")
lbl_nCardsToStudy = tk.Label(master=fr_settings, width=20, text="# cards to study", justify = tk.LEFT)
ent_nCardsToStudy = tk.Entry(master=fr_settings, width=10, justify=tk.RIGHT)
ent_nCardsToStudy.insert(tk.END, str(nCardsInDeck))

MODE_STUDY_CN2EN = 100
MODE_STUDY_EN2CN = 101
MODE_STUDY_BOTH  = 102
mode_study = tk.IntVar()
mode_study.set(MODE_STUDY_CN2EN)
lbl_modes = tk.Label(fr_settings, width=20, text="Practice Mode", justify = tk.LEFT)
rdb_cn2en = tk.Radiobutton(fr_settings, text="CN 2 EN".ljust(12), padx = 5, variable=mode_study, value=MODE_STUDY_CN2EN)
rdb_en2cn = tk.Radiobutton(fr_settings, text="EN 2 CN".ljust(12), padx = 5, variable=mode_study, value=MODE_STUDY_EN2CN)
rdb_both  = tk.Radiobutton(fr_settings, text="Both ways".ljust(12), padx = 5, variable=mode_study, value=MODE_STUDY_BOTH)

MODE_CARDSELECT_NEW = 100
MODE_CARDSELECT_ALL = 101
MODE_CARDSELECT_GOOD = 102
MODE_CARDSELECT_MEDIUM = 103
MODE_CARDSELECT_BAD    = 104
MODE_CARDSELECT_RATING = 105
mode_cardSelection = tk.IntVar()
mode_cardSelection.set(MODE_CARDSELECT_ALL)
lbl_cardSelect = tk.Label(fr_settings, width=20, text="Card Selection Mode", justify = tk.LEFT)
rdb_newCards = tk.Radiobutton(fr_settings, text="New Cards".ljust(12), padx = 5, variable=mode_cardSelection, value=MODE_CARDSELECT_NEW, bg="steelblue")
rdb_allCards = tk.Radiobutton(fr_settings, text="All Cards".ljust(12), padx = 5, variable=mode_cardSelection, value=MODE_CARDSELECT_ALL)
rdb_goodCards = tk.Radiobutton(fr_settings, text="Good Cards".ljust(12), padx = 5, variable=mode_cardSelection, value=MODE_CARDSELECT_GOOD, bg="green3")
rdb_mediumCards = tk.Radiobutton(fr_settings, text="Medium Cards".ljust(12), padx = 5, variable=mode_cardSelection, value=MODE_CARDSELECT_MEDIUM, bg="orange")
rdb_badCards = tk.Radiobutton(fr_settings, text="Bad Cards".ljust(12), padx = 5, variable=mode_cardSelection, value=MODE_CARDSELECT_BAD, bg="orange red")

fr_ratingSelect = tk.Frame(fr_settings)
rdb_singleRating = tk.Radiobutton(fr_ratingSelect, text="Only Rating:", padx = 0, variable=mode_cardSelection, value=MODE_CARDSELECT_RATING)
ratingSelect = tk.IntVar()
ratingSelect.set(1)
menu_ratingSelect = tk.OptionMenu(fr_ratingSelect, ratingSelect, 1,2,3,4,5,6)

btn_start = tk.Button(fr_settings, text="Start Practice", command=start_practice, height=1, relief=tk.RAISED)

lbl_vocab = tk.Label(fr_settings, width=20, text="Vocabulary - Rating Breakdown", fg="white", bg="blue",justify = tk.LEFT, height=2)
lbl_txtHeaderRating = tk.Label(fr_settings, width=20, text="en2cn   |   cn2en", justify = tk.LEFT)
lbl_txtRating1 = tk.Label(fr_settings, width=10, text="Rating 1", justify = tk.LEFT)
lbl_txtRating2 = tk.Label(fr_settings, width=10, text="Rating 2", justify = tk.LEFT)
lbl_txtRating3 = tk.Label(fr_settings, width=10, text="Rating 3", justify = tk.LEFT)
lbl_txtRating4 = tk.Label(fr_settings, width=10, text="Rating 4", justify = tk.LEFT)
lbl_txtRating5 = tk.Label(fr_settings, width=10, text="Rating 5", justify = tk.LEFT)
lbl_txtRating6 = tk.Label(fr_settings, width=10, text="Rating 6", justify = tk.LEFT)
lbl_txtTotal = tk.Label(fr_settings, width=10, text="Total", justify = tk.LEFT)
lbl_txtNew = tk.Label(fr_settings, width=10, text="New Cards", justify = tk.LEFT)

lbl_valRating1 = tk.Label(fr_settings, width=20, text="", justify = tk.LEFT, font=(None,8))
lbl_valRating2 = tk.Label(fr_settings, width=20, text="", justify = tk.LEFT, font=(None,8))
lbl_valRating3 = tk.Label(fr_settings, width=20, text="", justify = tk.LEFT, font=(None,8))
lbl_valRating4 = tk.Label(fr_settings, width=20, text="", justify = tk.LEFT, font=(None,8))
lbl_valRating5 = tk.Label(fr_settings, width=20, text="", justify = tk.LEFT, font=(None,8))
lbl_valRating6 = tk.Label(fr_settings, width=20, text="", justify = tk.LEFT, font=(None,8))
lbl_valTotal = tk.Label(fr_settings, width=20, text="", justify = tk.LEFT)
lbl_valNew = tk.Label(fr_settings, width=20, text="", justify = tk.LEFT)
list_lbl_valRatings = [lbl_valRating1,lbl_valRating2,lbl_valRating3,
                       lbl_valRating4,lbl_valRating5,lbl_valRating6]


# set the layout for the settings frame
lbl_nCardsToStudy.grid(row=0, column=0, sticky="w", padx=5, pady=5)
ent_nCardsToStudy.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

lbl_modes.grid(row=1, column=0, sticky="w", padx=5, pady=5)
rdb_cn2en.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
rdb_en2cn.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
rdb_both.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

lbl_cardSelect.grid(row=4, column=0, sticky="w", padx=5, pady=5)
rdb_newCards.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
rdb_allCards.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
rdb_goodCards.grid(row=6, column=1, sticky="ew", padx=5, pady=5)
rdb_mediumCards.grid(row=7, column=1, sticky="ew", padx=5, pady=5)
rdb_badCards.grid(row=8, column=1, sticky="ew", padx=5, pady=5)
fr_ratingSelect.grid(row=9, column=1, sticky="ew", padx=5, pady=5)
rdb_singleRating.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
menu_ratingSelect.grid(row=0, column=1, sticky="ew", padx=0, pady=0)
btn_start.grid(row=10, column=0, rowspan=1, columnspan=2, sticky="nsew",padx=5, pady=5)

lbl_vocab.grid(row=11, column=0, columnspan=2, sticky="nsew", padx=5, pady=(10,5))
lbl_txtHeaderRating.grid(row=12, column=1, columnspan=1, sticky="ew", padx=5, pady=5)
lbl_txtRating1.grid(row=13, column=0, sticky="ew", padx=5, pady=5)
lbl_txtRating2.grid(row=14, column=0, sticky="ew", padx=5, pady=5)
lbl_txtRating3.grid(row=15, column=0, sticky="ew", padx=5, pady=5)
lbl_txtRating4.grid(row=16, column=0, sticky="ew", padx=5, pady=5)
lbl_txtRating5.grid(row=17, column=0, sticky="ew", padx=5, pady=5)
lbl_txtRating6.grid(row=18, column=0, sticky="ew", padx=5, pady=5)
lbl_txtTotal.grid(row=19, column=0, sticky="ew", padx=5, pady=5)
lbl_txtNew.grid(row=20, column=0, sticky="ew", padx=5, pady=5)

lbl_valRating1.grid(row=13, column=1, sticky="ew", padx=5, pady=5)
lbl_valRating2.grid(row=14, column=1, sticky="ew", padx=5, pady=5)
lbl_valRating3.grid(row=15, column=1, sticky="ew", padx=5, pady=5)
lbl_valRating4.grid(row=16, column=1, sticky="ew", padx=5, pady=5)
lbl_valRating5.grid(row=17, column=1, sticky="ew", padx=5, pady=5)
lbl_valRating6.grid(row=18, column=1, sticky="ew", padx=5, pady=5)
lbl_valTotal.grid(row=19, column=1, sticky="ew", padx=5, pady=5)
lbl_valNew.grid(row=20, column=1, sticky="ew", padx=5, pady=5)

# ----- frame for card
fr_card  = tk.Frame(window, width=500, bg="grey22")
lbl_progress = tk.Label(fr_card, bg="blue" , fg="white", height=2, width=10)
# note that a lot of fonts are not suitable for chinese characters
# according to google, the following work well:
# Hiragino Sans GB , Microsoft Yahei [not found in tkinter] , Simhei [not found in tkinter]
lbl_card     = tk.Label(fr_card, bg="black", fg="white", height=18, width=40, relief=tk.GROOVE, font=("Hiragino Sans GB", 20))
#lbl_card     = tk.Label(fr_card, bg="black", fg="white", height=20, width=50, relief=tk.GROOVE, font=("Courier", 20))
btn_flip     = tk.Button(fr_card, text="Flip Card <SPACE>", height=2, width=50, command=flip_card)

# set the layout for the card frame
lbl_progress.grid(row=0,column=0, sticky="nw", padx=5, pady=5)
lbl_card.grid(row=1, column=0, sticky="nsew", padx=5)
btn_flip.grid(row=2, column=0, sticky="ews", padx=5, pady=5)

# ----- frame for classifying card
fr_classify = tk.Frame(window, width=150, bg="grey22")
btn_classify1 = tk.Button(fr_classify, text="[1] Incorrect, total blackout"     , anchor="w", width=30, bg="red3"     , command=assign_value_1)
btn_classify2 = tk.Button(fr_classify, text="[2] Incorrect, but familiar"       , anchor="w", width=30, bg="orangered", command=assign_value_2)
btn_classify3 = tk.Button(fr_classify, text="[3] Incorrect, but easy"           , anchor="w", width=30, bg="salmon1"  , command=assign_value_3)
btn_classify4 = tk.Button(fr_classify, text="[4] Correct  , but with struggle"  , anchor="w", width=30, bg="green2"   , command=assign_value_4)
btn_classify5 = tk.Button(fr_classify, text="[5] Correct  , but with hesitation", anchor="w", width=30, bg="green3"   , command=assign_value_5)
btn_classify6 = tk.Button(fr_classify, text="[6] Correct  , easy"               , anchor="w", width=30, bg="green4"   , command=assign_value_6)
list_btn_classify = [btn_classify1, btn_classify2, btn_classify3, btn_classify4, btn_classify5, btn_classify6]

# set the layout for the classification frame
btn_classify1.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_classify2.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_classify3.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
btn_classify4.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
btn_classify5.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
btn_classify6.grid(row=5, column=0, sticky="ew", padx=5, pady=5)

# ----- set the layout for the window
fr_settings.grid(row=0, column=0, sticky="ns")
fr_card.grid(row=0, column=1, sticky="ns")
fr_classify.grid(row=0, column=2, sticky="ns")

#########################################################################################
#     set up initial GUI look
#########################################################################################
# Set some initial values in GUI
lbl_progress["text"] = ""
str_welcome = "Welcome to my App - Go Forth and Study"
display_ratingBreakdown()
display_card(text=str_welcome)
disable_buttonsClassify()
disable_buttonFlip()
    
#########################################################################################    
#     Run the application
#########################################################################################
window.bind("<space>", keyshortcut_space)
window.mainloop()
