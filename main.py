from tkinter import *
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from math import *

TIMEFRAME_GAP = 6

# ------------------------------------------Functionality-------------------------------------------------------------
def save():
    try:
        player_json = json.load(open(user_dance_entry.get(), "r"))
        _data_ = json.load(open(dance_template_entry.get(), "r"))
        instructor_json = _data_["data"]
        body_section = _data_["poseSection"]

        def format_data(data):
            formatted_data = []
            for i in data:
                lista = []
                lista.append(i["lea"])
                lista.append(i["lha"])
                lista.append(i["lka"])
                lista.append(i["lsa"])
                lista.append(i["rea"])
                lista.append(i["rha"])
                lista.append(i["rka"])
                lista.append(i["rsa"])
                formatted_data.append(lista)
            return formatted_data

        def get_angle_list(angle, data):
            """takes angle and it's data set as input and returns a list of that angle"""
            angle_list = []
            for item in data:
                angle_list.append(item[angle])
            return angle_list

        def get_timestamp_list(data):
            """takes the data set as input and returns a list of it's timestamps"""
            timestamp_list = []
            for item in data:
                timestamp = item["timestamp"]
                timestamp_list.append(timestamp)
            del timestamp_list[-1]
            return timestamp_list

        def get_angle_difference(angle, player_data, template_data):
            """takes angle,player data and instructor data as input and returns the absolute angle difference"""
            player = get_angle_list(angle, player_data)
            instructor = get_angle_list(angle, template_data)
            angle_difference_list = []

            for i in range(0, len(player) - 1):
                six_angle_list = []

                for l in range(TIMEFRAME_GAP * (i + 1) - TIMEFRAME_GAP, TIMEFRAME_GAP * (i + 1)):
                    angle_difference = abs(instructor[l] - player[i])
                    six_angle_list.append(angle_difference)

                angle_difference_list.append(min(six_angle_list))
            return angle_difference_list

        formatted_template_data = format_data(instructor_json)
        formatted_player_data = format_data(player_json)

        def get_score(player_index, index, player_data, template_data):
            angle_sum = 0
            zerochecker1 = 0
            zerochecker2 = 0

            for i in player_data:
                for j in i:
                    zerochecker1 += j

            for i in template_data:
                for j in i:
                    zerochecker2 += j

            subtracted_angles_list = []
            score_angles_list = []
            score_GM_list = []
            count_above_40 = 0
            fun_value = 0

            if zerochecker1 != 0 and zerochecker2 != 0:
                for i in range(0, 8):
                    # index of dict isn't an integer
                    angle_diff = abs(player_data[player_index][i] - template_data[index][i])

                    # timestamp of template doesn't timestamp of player_data, playerdata[0][0]=200, templatedata[0][0]=33

                    if angle_diff > 1:
                        angle_diff = 1
                    subtracted_angles_list.append(angle_diff)
                    scoreX = subtracted_angles_list[i]
                    # fun_value=100*(1/(1+pow((scoreX/0.5),4.5)))
                    fun_value = (-200 * pow(scoreX, 3.5)) + 100
                    if fun_value < 0:
                        fun_value = 0
                    score_angles_list.append(fun_value)

                    # fun_value is a float, why do we need to max() it

                    if i == 2:
                        # left hip * left knee
                        scrA = score_angles_list[1]
                        scrB = score_angles_list[2]
                        score_GM_list.append(sqrt(scrA * scrB))

                    if i == 3:
                        # left elbow* left shoulder
                        scrA = score_angles_list[0]
                        scrB = score_angles_list[3]
                        score_GM_list.append(sqrt(scrA * scrB))
                    if i == 6:
                        # right hip * right knee
                        scrA = score_angles_list[5]
                        scrB = score_angles_list[6]
                        score_GM_list.append(sqrt(scrA * scrB))

                    if i == 7:
                        # left elbow* left shoulder
                        scrA = score_angles_list[4]
                        scrB = score_angles_list[7]
                        score_GM_list.append(sqrt(scrA * scrB))

                if body_section == "upperbody":
                    angle_sum = (score_GM_list[1] + score_GM_list[3]) / 2

                elif body_section == "lowerbody":
                    angle_sum = (score_GM_list[0] + score_GM_list[2]) / 2

                elif body_section == "fullbody":

                    for i in range(0, 4):
                        if score_GM_list[i] > 40:
                            count_above_40 += 1

                        angle_sum += score_GM_list[i]

                    if count_above_40 > 2:
                        angle_sum /= 4
                    else:
                        angle_sum = 0
            return angle_sum

        def get_energy_score2(w, x, y, z, player_idx, player_idx1, template_idx, template_idx1, player_data, template_data,
                              max):
            no_move_count = 0
            trainer_delta = []
            user_delta = []
            threshold = 0.174
            tcount = 0
            ucount = 0

            trainer_delta.append(abs(template_data[template_idx][w] - template_data[template_idx1][w]))
            trainer_delta.append(abs(template_data[template_idx][x] - template_data[template_idx1][x]))
            trainer_delta.append(abs(template_data[template_idx][y] - template_data[template_idx1][y]))
            trainer_delta.append(abs(template_data[template_idx][z] - template_data[template_idx1][z]))

            user_delta.append(abs(player_data[player_idx][w] - player_data[player_idx1][w]))
            user_delta.append(abs(player_data[player_idx][x] - player_data[player_idx1][x]))
            user_delta.append(abs(player_data[player_idx][y] - player_data[player_idx1][y]))
            user_delta.append(abs(player_data[player_idx][z] - player_data[player_idx1][z]))

            for i in trainer_delta:
                if i > threshold:
                    tcount += 1

            if tcount < 1:
                return 100

            for i in user_delta:
                if i > threshold:
                    ucount += 1

            if ucount < 1:
                no_move_count += 1

                if no_move_count > 10:
                    return 0
                else:
                    return 100
            else:
                no_move_count = 0
                return 100

        def get_energy_score1(player_data, template_data, max, player_idx, player_idx1, template_idx, template_idx1):
            no_move_count = 0
            trainer_delta = []
            user_delta = []
            threshold = 0.174
            tcount = 0
            ucount = 0

            if body_section == "upperbody":
                return get_energy_score2(0, 3, 4, 7, player_idx, player_idx1, template_idx, template_idx1, player_data,
                                         template_data, max)

            elif body_section == "lowerbody":
                return get_energy_score2(1, 2, 5, 6, player_idx, player_idx1, template_idx, template_idx1, player_data,
                                         template_data, max)
            else:
                for i in range(0, 8):
                    trainer_delta.append(abs(template_data[template_idx][i] - template_data[template_idx1][i]))
                    if trainer_delta[i] > threshold:
                        tcount += 1

                if tcount < 3:
                    return 100

                for i in range(0, 8):
                    user_delta.append(abs(player_data[player_idx][i] - player_data[player_idx1][i]))
                    if user_delta[i] > threshold:
                        ucount += 1

                if ucount < 3:
                    no_move_count += 1

                    if no_move_count > 10:
                        return 0
                    else:
                        return 100
                else:
                    no_move_count = 0
                    return 100
        s_index=[]
        def get_highest_score(player_data, template_data, count):
            # print(f"count={count}")
            idx=0
            max = 0
            energy_score = 0
            skipper=0
            i = int(count / 6 - 1)
            if i == 0:
                p = 5
            elif i==1:
                p = 11
            elif count+17>len(template_data)-1:
                p=len(template_data)-1-count
            else:
                p=17

                for l in range(count - p -1, count + 17):
                    if skipper==2:
                        angle_score = get_score(i,l , player_data, template_data)
                        if angle_score >= max:
                            max = angle_score
                            idx=l
                            if i > 0:
                                energy_score = get_energy_score1(player_data, template_data, max, i, i - 1, count, count - 6)
                        skipper=0
                    else:
                        skipper+=1
                s_index.append(idx)
            return ((max * energy_score) / 100)

        def get_score_list():
            score_list = []
            for count in range(0, len(formatted_template_data), 6):
                score_list.append(get_highest_score(formatted_player_data, formatted_template_data, count))
            print(s_index)
            #        print(sum(score_list)/len(formatted_player_data))
            return score_list

        def get_points():
            score = sum(get_score_list()) / len(formatted_player_data)
            return score
        print(formatted_player_data)
        #
        #
        #
        #                                 -------------plot---------------
        #
        #
        #
        #

        def plot_angle(angle, player_data, template_data, subplot, figure, ):
            """Takes the angle, player dance, instructor dance, the subplot integer and plots the graph"""
            plot = figure.add_subplot(subplot, )
            figure.set_facecolor("cornflowerblue")
            plot.set_title(f"{angle.upper()}-Timestamp Graph", fontsize=14)
            plot.plot(get_timestamp_list(player_data), get_angle_difference(angle, player_data, template_data, ),
                      color="k", )
            plot.set_xlabel("Time")
            plot.set_ylabel(angle.upper())

        def plot_score(figure, subplot, player_data):
            plot = figure.add_subplot(subplot)
            figure.set_facecolor("cornflowerblue")
            plot.set_title(f"Score={int(get_points())}", fontsize=14)
            plot.plot(get_timestamp_list(player_data), get_score_list(), color="k", )
            plot.set_xlabel("Time")
            plot.set_ylabel("Score")

        rsa_fig = Figure(figsize=(10, 5), dpi=100, )
        rka_fig = Figure(figsize=(10, 5), dpi=100, )
        rea_fig = Figure(figsize=(10, 5), dpi=100, )
        rha_fig = Figure(figsize=(10, 5), dpi=100, )
        lsa_fig = Figure(figsize=(10, 5), dpi=100, )
        lka_fig = Figure(figsize=(10, 5), dpi=100, )
        lea_fig = Figure(figsize=(10, 5), dpi=100, )
        lha_fig = Figure(figsize=(10, 5), dpi=100, )
        score_fig = Figure(figsize=(10, 5), dpi=100)

        plot_score(score_fig, 111, player_json)
        frame9 = Frame(second_frame, pady=20, padx=20, bg="cornflowerblue")
        canvas9 = FigureCanvasTkAgg(score_fig, master=second_frame, )
        canvas9.draw()
        canvas9.get_tk_widget().pack()
        toolbar9 = NavigationToolbar2Tk(canvas9, frame9)
        toolbar9.config(bg="cornflowerblue")
        toolbar9.pack()
        frame9.pack()

        plot_angle("rsa", player_json, instructor_json, 111, rsa_fig, )
        frame1 = Frame(second_frame, bg="cornflowerblue")
        canvas1 = FigureCanvasTkAgg(rsa_fig, master=second_frame, )
        canvas1.draw()
        canvas1.get_tk_widget().pack()
        toolbar1 = NavigationToolbar2Tk(canvas1, frame1)
        toolbar1.config(bg="cornflowerblue")
        toolbar1.pack()
        frame1.pack()

        plot_angle("rha", player_json, instructor_json, 111, rha_fig, )
        frame2 = Frame(second_frame, bg="cornflowerblue")
        canvas2 = FigureCanvasTkAgg(rha_fig, master=second_frame, )
        canvas2.draw()
        canvas2.get_tk_widget().pack()
        toolbar2 = NavigationToolbar2Tk(canvas2, frame2, )
        toolbar2.config(bg="cornflowerblue")
        toolbar2.pack()
        frame2.pack()

        plot_angle("rea", player_json, instructor_json, 111, rea_fig, )
        frame3 = Frame(second_frame, bg="cornflowerblue")
        canvas3 = FigureCanvasTkAgg(rea_fig, master=second_frame, )
        canvas3.draw()
        canvas3.get_tk_widget().pack()
        toolbar3 = NavigationToolbar2Tk(canvas3, frame3)
        toolbar3.config(bg="cornflowerblue")
        toolbar3.pack()
        frame3.pack()

        plot_angle("rka", player_json, instructor_json, 111, rka_fig, )
        frame4 = Frame(second_frame, bg="cornflowerblue")
        canvas4 = FigureCanvasTkAgg(rka_fig, master=second_frame, )
        canvas4.draw()
        canvas4.get_tk_widget().pack()
        toolbar4 = NavigationToolbar2Tk(canvas4, frame4)
        toolbar4.config(bg="cornflowerblue")
        toolbar4.pack()
        frame4.pack()

        plot_angle("lsa", player_json, instructor_json, 111, lsa_fig, )
        frame5 = Frame(second_frame, bg="cornflowerblue")
        canvas5 = FigureCanvasTkAgg(lsa_fig, master=second_frame, )
        canvas5.draw()
        canvas5.get_tk_widget().pack()
        toolbar5 = NavigationToolbar2Tk(canvas5, frame5)
        toolbar5.config(bg="cornflowerblue")
        toolbar5.pack()
        frame5.pack()

        plot_angle("lha", player_json, instructor_json, 111, lha_fig, )
        frame6 = Frame(second_frame, bg="cornflowerblue")
        canvas6 = FigureCanvasTkAgg(lha_fig, master=second_frame, )
        canvas6.draw()
        canvas6.get_tk_widget().pack()
        toolbar6 = NavigationToolbar2Tk(canvas6, frame6)
        toolbar6.config(bg="cornflowerblue")
        toolbar6.pack()
        frame6.pack()

        plot_angle("lea", player_json, instructor_json, 111, lea_fig, )
        frame7 = Frame(second_frame, bg="cornflowerblue")
        canvas7 = FigureCanvasTkAgg(lea_fig, master=second_frame, )
        canvas7.draw()
        canvas7.get_tk_widget().pack()
        toolbar7 = NavigationToolbar2Tk(canvas7, frame7)
        toolbar7.config(bg="cornflowerblue")
        toolbar7.pack()
        frame7.pack()

        plot_angle("lka", player_json, instructor_json, 111, lka_fig, )
        frame8 = Frame(second_frame, bg="cornflowerblue")
        canvas8 = FigureCanvasTkAgg(lka_fig, master=second_frame, )
        canvas8.draw()
        canvas8.get_tk_widget().pack()
        toolbar8 = NavigationToolbar2Tk(canvas8, frame8)
        toolbar8.config(bg="cornflowerblue")
        toolbar8.pack()
        frame8.pack()


        #                           -------------------Clear Button--------------------
        def destroy_canvas(canvas, frame):
            canvas.get_tk_widget().destroy()
            frame.destroy()

        def clear():
            destroy_canvas(canvas1, frame1)
            destroy_canvas(canvas2, frame2)
            destroy_canvas(canvas3, frame3)
            destroy_canvas(canvas4, frame4)
            destroy_canvas(canvas5, frame5)
            destroy_canvas(canvas6, frame6)
            destroy_canvas(canvas7, frame7)
            destroy_canvas(canvas8, frame8)
            destroy_canvas(canvas9, frame9)
            clear_button.destroy()

        clear_button = Button(second_frame, text="             CLEAR                ", command=clear,
                              font=("arial", 16, "bold"), pady=5, padx=20)
        clear_button.pack(side=BOTTOM)

    #                                        -------------------------------

        user_dance_entry.delete(0, END)
        dance_template_entry.delete(0, END)
    except FileNotFoundError:
        open_popup("Invalid File Name!")
    except IndexError:
        try:
            def destroy_canvas(canvas, frame):
                canvas.get_tk_widget().destroy()
                frame.destroy()
            def clear():
                destroy_canvas(canvas1, frame1)
                destroy_canvas(canvas2, frame2)
                destroy_canvas(canvas3, frame3)
                destroy_canvas(canvas4, frame4)
                destroy_canvas(canvas5, frame5)
                destroy_canvas(canvas6, frame6)
                destroy_canvas(canvas7, frame7)
                destroy_canvas(canvas8, frame8)
                clear()
        finally:
            open_popup("User dance does "
                       "not match template!")


# --------------------------------------------UI SETUP---------------------------------------------------------------
#                             --------------WINDOW SETUP--------------
window = Tk()
window.title("Dance Data Analaysis")
window.minsize(width=1000, height=800)
window.config(bg="white")

main_frame = Frame(window, bg="cornflowerblue")
main_frame.pack(fill=BOTH, expand=1)
my_canvas = Canvas(main_frame, bg="cornflowerblue")
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)
my_canvas.configure(yscrollcommand=scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
second_frame = Frame(my_canvas, bg="cornflowerblue")
my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

#                        -----------------Widget setup----------------

user_dance_label = Label(second_frame, text="Enter file name:       ", font=("arial", 12,), bg="cornflowerblue")
user_dance_label.pack()

user_dance_entry = Entry(second_frame, width=35)
user_dance_entry.pack()

dance_choice_label = Label(second_frame, text="Choose your dance:", font=("arial", 12,), bg="cornflowerblue")
dance_choice_label.pack()

dance_template_entry = Entry(second_frame, width=35)
dance_template_entry.pack()


# radiobuttons
def radio_used():
    if radio_state.get() == 1:
        dance_template_entry.delete(0, END)
        dance_template_entry.insert(0, "Jugnu template.json")
    if radio_state.get() == 2:
        dance_template_entry.delete(0, END)
        dance_template_entry.insert(0, "Cham Cham template.json")
    if radio_state.get() == 3:
        dance_template_entry.delete(0, END)
        dance_template_entry.insert(0, "Raatan Lambiyan template.json")
    if radio_state.get() == 4:
        dance_template_entry.delete(0, END)
        dance_template_entry.insert(0, "naaja Template.json")


radio_state = IntVar()
jugnu = Radiobutton(second_frame, text="Jugnu                   ", value=1, variable=radio_state, command=radio_used,
                    bg="cornflowerblue")
jugnu.pack()

chamcham = Radiobutton(second_frame, text="Cham Cham        ", value=2, variable=radio_state, command=radio_used,
                       bg="cornflowerblue")
chamcham.pack()

raatan_lambiyan = Radiobutton(second_frame, text="Raatan Lambiyan", value=3, variable=radio_state, command=radio_used,
                              bg="cornflowerblue")

raatan_lambiyan.pack()

najja_najja = Radiobutton(second_frame, text="Najja Najja           ", value=4, variable=radio_state,
                          command=radio_used, bg="cornflowerblue")
najja_najja.pack()

confirm_button = Button(second_frame, text="    Plot   ", command=save, bg="white",padx=20,pady=5,font=("arial",14,"bold"))
confirm_button.pack()

def open_popup(label_text):
    top=Toplevel(second_frame)
    top.geometry("500x250")
    top.title("ERROR")
    label=Label(top,text=label_text,font=("arial",16,"bold"))
    label.pack()

window.mainloop()
