import utils

from utils import commit
from utils import cursor


class Editor:

    def __init__(self, eid):
        self.eid = eid

    def handle(self):
        print( "Successfully login as an editor\n" )
        cmdDict = {
            "add": self.addMovieAndCasts,
            "help": self.help,
            "update": self.update,
        }

        while True:
            try:
                line = input(f"{self.eid}\n$ ").strip()

                print()

                if not line: continue

                # Separator of a command line is "|"
                tokens = line.split('|')
                cmd = tokens[0]

                if cmd in cmdDict:
                    func = cmdDict[cmd]
                    args = tokens[1:] if len(tokens) > 1 else []
                    try:
                        func(*args)
                    except TypeError as tError:
                        print(tError)
                        print(f"{cmd}: invalid arguments")
                elif cmd == "exit" or cmd == "quit":
                    quit(0)
                elif cmd == "logout":
                    print( "logout successfully" )
                    return
                else:
                    print(f"{line}: command not found")
            except KeyboardInterrupt:
                quit(0)

    def addMovieAndCasts(self, mid, title, year, runtime):
        try:
            assert utils.isValidInt(mid), "Invalid movie id"
            assert utils.isValidText(title), "Invalid title"
            assert utils.isValidYear(year), "Invalid year"
            assert utils.isValidInt(runtime), "Invalid runtime"
        except AssertionError as ae:
            print(ae)
            return

        if self.hasMovie(mid):
            print(f"movie {mid} exists in the database")
            return

        self.addMovie(mid, title, year, runtime)

        print(f"Provide a list of cast members and their roles for movie {mid}")
        while True:
            try:
                print("Ctrl-C / Ctrl-Z to aboard current process")
                pid = input("Enter the id of the cast member: ").strip()

                try:
                    assert utils.isValidInt(pid), "Invalid pid"
                except AssertionError as ae:
                    print(ae)
                    continue

                pid = int(pid)
                if self.hasMember(pid):
                    self.addCast(mid, pid)
                else:
                    print(f"Member p{pid} doesn't exist in the database")
                    ans = input(f"Add this member p{pid} into the database(y/n)?").strip()
                    if ans.lower() == "y":
                        name = input("name: ").strip()
                        birthYear = input("birth year: ").strip()

                        try:
                            assert utils.isValidText(name), "Invalid name"
                            assert utils.isValidYear(birthYear), "Invalid year"
                        except AssertionError as ae:
                            print(ae)
                            continue

                        self.addMember(pid, name, birthYear)

            except KeyboardInterrupt as kI:
                print("Aboard current task")
                break

    def addCast(self, mid, pid):
        mid = int(mid)
        pid = int(pid)

        if self.hasRoleOf(mid, pid):
            print(f"Member p{pid} has a role in movie {mid}. "
                  f"A cast member cannot take more than one role in the same movie")
        else:
            name, birthYear = self.getMember(pid)

            print(f"Member p{pid} information:\n"
                  f"{name}\n"
                  f"birth year: {birthYear}")

            try:
                role = input(
                    f"Enter a role for member p{pid} in movie {mid} "
                    f"or reject this request (type reject)")
                if role.lower() == "reject":
                    return
                else:

                    try:
                        assert utils.isValidText(role), "Invalid role"
                    except AssertionError as ae:
                        print(ae)
                        return

                    self.addRole(mid, pid, role)
            except KeyboardInterrupt as kInterp:
                print("Aboard current task")

    def addMember(self, pid, name, birthYear):
        birthYear = int(birthYear)
        pid = f"p{pid}"

        cursor.execute("insert into moviePeople values (?, ?, ?)",
                       (pid, name, birthYear,))
        commit()

        print(f"Member {pid} is added into the database")

    def addMovie(self, mid, title, year, runtime):
        mid = int(mid)
        year = int(year)
        runtime = int(runtime)

        cursor.execute("insert into movies values (?, ?, ?, ?)",
                       (mid, title, year, runtime,))
        commit()

        print(f"movie {mid} is added into the database")

    def addRole(self, mid, pid, role):
        pid = f"p{pid}"
        cursor.execute("insert into casts values (?, ?, ?)", (mid, pid, role,))

        commit()

        print(f"Add member {pid} as a cast in movie {mid} with role \"{role}\"")

    def help(self, args):
        pass

    def displayMoviePair(self, results):
        for index, result in enumerate(results):
            mid1 = int(result[0])
            mid2 = int(result[1])
            num = int(result[2])

            score, isIn = self.inRecommendations(mid1, mid2)

            print(f"{index}. ({mid1}, {mid2}) | "
                  f"{num} watched | "
                  f"score: {score} | "
                  f"{'In Recommendation' if isIn else 'Not In Recommendation'}")

    def selectMoviePair(self, results):
        while True:
            try:
                index = input("Please select one of movie pairs: ").strip()

                assert utils.isValidInt(index) \
                       and 0 < int(index) <= len(results), "Invalid index"

                index = int(index)

                result = results[index-1]

                mid1 = int(result[0])
                mid2 = int(result[1])
                score, isIn = self.inRecommendations(mid1, mid2)
                if isIn:
                    ans = input("Update score / Remove from recommendation(u/r)?").strip()

                    if ans.lower() == "u":
                        self.updateScore(mid1, mid2)
                    elif ans.lower() == "r":
                        self.removeRecommendation(mid1, mid2)
                else:
                    ans = input("Add to recommendation(y/n)?").strip()
                    if ans.lower() == "y":
                        self.addRecommendation(mid1, mid2)

            except AssertionError as ae:
                print(ae)
            except KeyboardInterrupt as kI:
                print("Aboard current task")
                break

    def update(self, option):
        options = ["-a", "-h", "-m", "-y"]

        if not option:  # no argument provided to the command
            self.updateHelp()
        else:
            if option in options:
                if option == "-h":
                    self.updateHelp()
                else:
                    results = self.selectWatchedBy(option)
                    if not results:
                        return

                    self.displayMoviePair(results)
                    self.selectMoviePair(results)
            else:
                print(f"update: unknown option -- {option}")
                print("Try 'update -h' for more information.")

    def addRecommendation(self, mid1, mid2):
        while True:
            try:
                score = input("Enter the score (0 ~ 1.0): ").strip()
                assert 0 <= float(score) <= 1, "Invalid score"

                score = float(score)

                cursor.execute("insert into recommendations values (?, ?, ?)",
                               (mid1, mid2, score))

                commit()

                print("Recommendation was added")
            except KeyboardInterrupt as kI:
                print("Aboard current task")
                break
            except ValueError:
                print("Invalid score")
            except AssertionError as ae:
                print(ae)

    def removeRecommendation(self, mid1, mid2):
        cursor.execute("delete from recommendations where watched = ? and recommended = ?",
                       (mid1, mid2))
        commit()

        print("Recommendation was deleted")

    def updateScore(self, mid1, mid2):
        while True:
            try:
                score = input("Enter the score (0 ~ 1.0): ").strip()
                assert 0 <= float(score) <= 1, "Invalid score"

                score = float(score)

                cursor.execute("update recommendations set score = ? "
                               "where watched = ? "
                               "and recommended = ?", (score, mid1, mid2))
                commit()

                print("Score was updated")
            except KeyboardInterrupt as kI:
                print("Aboard current task")
                break
            except ValueError:
                print("Invalid score")
            except AssertionError as ae:
                print(ae)

    def addHelp(self):
        print("usage: add [<options>] [arguments]")
        print("-m\t add a movie [arguments] = [mid]|[title]|[year}|[runtime]")
        print("-c\t add a cast member [arguments] = [mid]|[pid]")
        print("-M\t add a movie person [arguments] = [pid]|[name]|[birthYear]")

    def updateHelp(self):
        pass

    def selectWatchedBy(self, option):
        options = {
            "-a": " ",
            "-m": " and s.sdate > datetime('now', '-30 days') ",
            "-y": " and s.sdate > datetime('now', '-365 days') ",
        }

        selector = options[option]

        subquery = f"(select w2.cid, w2.mid " + \
                   f"from movies m, sessions s, watch w2 " + \
                   f"where m.mid = w2.mid " + \
                   f"and w2.duration >= m.runtime * 0.5 " + \
                   f"and w2.sid = s.sid" + f"{selector}" + \
                   f"group by w2.cid, w2.mid) as w2"

        query = f"select w1.mid, w2.mid, count(distinct w1.cid) as 'number of customers' " + \
                f"from movies m, sessions s, watch w1, {subquery} " + \
                f"where m.mid = w1.mid " + \
                f"and w1.duration >= m.runtime * 0.5 " + \
                f"and w1.sid = s.sid " + \
                f"{selector}" + \
                f"and w1.cid == w2.cid " + \
                f"and w1.mid <> w2.mid " + \
                f"group by w1.mid, w2.mid " + \
                f"order by count(distinct w1.cid) desc"

        result = cursor.execute(query).fetchall()

        return result

    def hasMovie(self, mid):
        result = cursor.execute("select * from movies where mid = ?",
                                (mid,)).fetchone()

        if result:
            return True

        return False

    def hasMember(self, pid):
        pid = f"p{pid}"
        result = cursor.execute("select * from moviePeople where pid = ?",
                                (pid,)).fetchone()

        if result:
            return True

        return False

    def hasRoleOf(self, mid, pid):
        pid = f"p{pid}"
        result = cursor.execute("select count(*) from casts where mid = ? and pid = ?",
                                (mid, pid,)).fetchone()

        if result[0] >= 1:
            return True

        return False

    def inRecommendations(self, mid1, mid2):
        result = cursor.execute("select score from recommendations r "
                                "where r.watched = ? and r.recommended = ?",
                                (mid1, mid2)).fetchone()
        if result:
            return result[0], True

        return 'No Score', False

    def getMember(self, pid):
        pid = f"p{pid}"
        result = cursor.execute("select name, birthYear from moviePeople where pid = ?",
                                (pid,)).fetchone()

        name = result[0]
        birthYear = result[1]

        return name, birthYear
