import json
import requests
import tkinter as tk
import concurrent.futures
import webbrowser

godsidlist = []
godsnamelist = []
godid = ""
enemyindex = []
enemyidlist = []
widgetflg = False
def main():

# リスト画面作成
    def create_list():
        url = "https://ai-battle-of-gods.bluepen.page/ranking"

        try:
            response = requests.get(url)
            response.encoding = response.apparent_encoding
            if response.status_code != 200:
                return False
        except requests.RequestException as e:
            return False
        listdata = response.text
        finds = listdata.find('"responses":')
        if finds < 0:
            return False
        finde = listdata.find(']',finds)
        if finde < 0:
            return False
        finds += 12
        finde += 1
        wkstr = listdata[finds:finde]
        '''
        with open('test.txt', 'w', encoding="utf-8") as iofile:
            iofile.write(wkstr)

        with open('test.txt', 'r', encoding="utf-8") as iofile:
            wkstr = iofile.read()
        '''

        json_data = json.loads(wkstr)
        global godsidlist
        global godsnamelist
        for k in json_data:
            godsidlist.append(k["id"])
            godsnamelist.append(k["name"])
            godsname_lst.insert("end", k["name"])
            
        count_txt.set(f"Rank 0/{len(godsnamelist)+1}")

# 戦績画面作成
    def set_battle(event):
        global godid
        godindex = godsname_lst.curselection()[0]
        godrank = godindex+1
        godid = godsidlist[godindex]
        godname = godsnamelist[godindex]
        godscnt = len(godsidlist) + 1
        print("ID:",godid,"/ Name:",godname,"/ Rank:",godrank)

        url = f"https://ai-battle-of-gods.bluepen.page/c/{godid}"
        battle_lbl.configure(text=godname)
        status_txt.set(f"{godname} [闘神ID:{godid}]")
        count_txt.set(f"Rank {godrank}/{godscnt}")
        try:
            response = requests.get(url)
            response.encoding = response.apparent_encoding
            if response.status_code != 200:
                return False
        except requests.RequestException as e:
            return False
        listdata = response.text
        finds = listdata.find('"battles":')
        if finds < 0:
            return False
        finde = listdata.find(']',finds)
        if finde < 0:
            return False
        finds += 10
        finde += 1
        wkstr = listdata[finds:finde]
        '''
        with open(f'{godid}.txt', 'w', encoding="utf-8") as iofile:
            iofile.write(wkstr)
        '''
        json_data = json.loads(wkstr)

        # 古いリスト削除
        global widgetflg
        global enemyindex
        if widgetflg:
            # リストの古い勝率消去
            for i in enemyindex:
                godsname_lst.delete(i)
                godsname_lst.insert(i, godsnamelist[i])
            battleenemy_lst.delete(0, tk.END)
            enemyindex = []
        widgetflg = True

        godlist = {}
        # 戦績表示
        cntbattle = len(json_data)
        for k in json_data:
            # 対戦相手データ
            if k["player1_id"] == godid:
                enemyid = k["player2_id"]
                enemyname = k["player2_name"]
            else:
                enemyid = k["player1_id"]
                enemyname = k["player1_name"]
            
            # 複数の対戦履歴がある場合
            if enemyid in godlist:
                godlist[enemyid]["battle"] += 1
                if k["winner_id"] == godid:
                    godlist[enemyid]["win"] += 1
                else:
                    godlist[enemyid]["lost"] += 1
            else:
                if k["winner_id"] == godid:
                    d = dict(
                        name = enemyname,
                        battle = 1,
                        win = 1,
                        lost = 0
                    )
                else:
                    d = dict(
                        name = enemyname,
                        battle = 1,
                        win = 0,
                        lost = 1
                    )
                godlist[enemyid] = d
        global enemyidlist

        cntenemy = len(godlist)
        cntwin = 0
        cntlost = 0
        for k in godlist:
            cntwin += godlist[k]["win"]
            cntlost += godlist[k]["lost"]
            enemyidlist.append(k)
            winrate = f'{round(godlist[k]["win"] / godlist[k]["battle"]*100)}%'
            battleenemy_lst.insert("end", f'{godlist[k]["name"]}  {godlist[k]["win"]} Win / {godlist[k]["lost"]} Lost  勝率 : {winrate}')
            try:
                # エネミーIDのindexを保存しておく
                enemyidingodslist = godsidlist.index(k)
                enemyindex.append(enemyidingodslist)
                godsname_lst.delete(enemyidingodslist)
                godsname_lst.insert(enemyidingodslist, f'{godlist[k]["name"]}  勝率 : {winrate}')
            except ValueError:
                print("Error EnemyID:",k)
                pass

        winrate = round(cntwin / (cntwin + cntlost) * 100)
        print(f"対戦数:{cntbattle} 対戦相手:{cntenemy} 勝利:{cntwin} 敗北:{cntlost} 勝率:{winrate}")
        rate_lbl.configure(text=f"対戦数:{cntbattle} 対戦相手:{cntenemy} 勝利:{cntwin} 敗北:{cntlost} 勝率:{winrate}%")

            
# UI
    root = tk.Tk()
    root.title("AI Battle - Match results tool")
    root.geometry("800x800")

    #ステータスバー
    status_frame = tk.Frame(root, bd = 1, relief = tk.SUNKEN)
    status_frame.pack(side = tk.BOTTOM, fill = tk.X, padx = 5, pady = 5)

    status_txt = tk.StringVar()
    status_txt.set("Ready")
    status_label = tk.Label(status_frame, textvariable = status_txt)
    status_label.pack(side = tk.LEFT, padx=2, pady=2)
    count_txt = tk.StringVar()
    status_label = tk.Label(status_frame, textvariable=count_txt)
    status_label.pack(side="right", padx=2, pady=2)

    # リスト
    gods_frm = tk.Frame(root, width=340)
    gods_frm.propagate(False)
    gods_frm.pack(side="left",fill="both")
    gods_lbl = tk.Label(gods_frm, text="闘神一覧")
    gods_lbl.pack(side="top", fill="x")

    gods_scrollbar = tk.Scrollbar(gods_frm, orient="vertical")
    gods_scrollbar.pack(side='right', fill="y")
    godsname_lst =tk.Listbox(gods_frm, width=60, relief="flat", selectmode="single")
    godsname_lst.bind("<<ListboxSelect>>", set_battle)
    godsname_lst.pack(side="left",fill="both", padx=5)
    godsname_lst.config(yscrollcommand=gods_scrollbar.set)
    gods_scrollbar.configure(command=godsname_lst.yview)

# 戦績
    battle_frm = tk.Frame(root)
    battle_frm.pack(side="top", fill="both", expand=True)
    battle_lbl = tk.Label(battle_frm, text="闘神を選択してください")
    battle_lbl.pack(side="top", fill="x")
    rate_lbl = tk.Label(battle_frm, text="")
    rate_lbl.pack(side="bottom", fill="x")

    def battle_webopen(event):
        selectenemyid = enemyidlist[battleenemy_lst.curselection()[0]]
        print(selectenemyid)
        global godid
        webbrowser.open(f'https://ai-battle-of-gods.bluepen.page/vs/{godid}/{selectenemyid}',autoraise=True)

    battle_scrollbar = tk.Scrollbar(battle_frm, orient="vertical")
    battle_scrollbar.pack(side="right", fill="y")
    battleenemy_lst =tk.Listbox(battle_frm, selectmode="single", relief="flat")
    battleenemy_lst.bind("<<ListboxSelect>>", battle_webopen)
    battleenemy_lst.pack(side="top", fill="both", padx=5, expand=True)
    battleenemy_lst.config(yscrollcommand=battle_scrollbar.set)
    battle_scrollbar.configure(command=battleenemy_lst.yview)

    create_list()
    root.mainloop()

if __name__ == "__main__":
    main()