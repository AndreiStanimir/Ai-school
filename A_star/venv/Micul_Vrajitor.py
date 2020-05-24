from copy import deepcopy
import numpy as np
import time

inf = 9999


class Nod:
    def __init__(self, matrix, h):
        self.matrix = matrix
        self.h = h

    def __str__(self):
        return "({}, h={})".format(self.matrix, self.h)

    def __repr__(self):
        return f"({self.matrix[:]}, h={self.h})"


class Wizard:
    # id_counter = 1

    def __init__(self, x, y, shoe_color, shoe_durability=3, h=0, desaga='', hasStone=False):
        self.shoe_color = shoe_color
        self.shoe_durability = shoe_durability
        self.reserve_color = ''
        self.reserve_durability = 0
        self.h = h
        self.hasStone = hasStone
        self.action = ''
        self.x = x
        self.y = y
        # self.id = Wizard.id_counter
        self.prev_shoe_positions = []

        # Wizard.id_counter += 1
        self.nr_pas = 0

    def FoundShoes(self, color):
        # se apeleaza cand vrajitorul ajunde la o pereche de papuci
        # returneaza o lista de vrajitori, fiecare vrajitor alege sa faca ceva diferit
        wizards = []
        if self.shoe_durability == 0:
            wizard = deepcopy(self)
            # wizard.id = Wizard.id_counter
            # Wizard.id_counter += 1

            wizard.prev_shoe_positions.append((wizard.x, wizard.y))
            wizard.shoe_color = color
            wizard.shoe_durability = 3
            wizard.action += ("A gasit cizme " + color + " si le pune in picoare\n")
            wizards.append(wizard)
            return wizards
        if self.reserve_color == '':  # deseaga goala
            wizard = deepcopy(self)
            # wizard.id = Wizard.id_counter
            # Wizard.id_counter += 1
            wizard.prev_shoe_positions.append((wizard.x, wizard.y))

            wizard.reserve_color = color
            wizard.reserve_durability = 3
            wizard.action += ("A gasit cizme " + color + " si le pune in deseaga.\n")
            wizards.append(wizard)
            return wizards
            # self.action+=

        if self.reserve_color == color and self.reserve_durability != 3:  #
            wizard = deepcopy(self)
            # wizard.id = Wizard.id_counter
            # Wizard.id_counter += 1
            wizard.prev_shoe_positions.append((wizard.x, wizard.y))

            wizard.reserve_color = color
            wizard.reserve_durability = 3
            wizard.action += ("Inlocuieste cizmele din deseaga " + color + ".\n")
            wizards.append(wizard)
        elif self.shoe_color == color and self.shoe_durability != 3:
            wizard = deepcopy(self)
            # wizard.id = Wizard.id_counter
            # Wizard.id_counter += 1
            wizard.prev_shoe_positions.append((wizard.x, wizard.y))
            wizard.shoe_durability = 3
            wizard.action += ("Inlocuieste cizmele din picioare " + color + ".\n")
            wizards.append(wizard)
        return wizards

    def __repr__(self):
        return self.action

    def __eq__(self, other):
        # am vrut sa folosesc id unic pentru comparare, nu am reusit :(
        return self.hasStone == other.hasStone and self.shoe_durability == other.shoe_durability and self.x == other.x and self.y == other.y
        # return self.id == other.id


class Cave:
    # colors_matrix
    # artifacts_matrix
    # self.euristica_aleasa = None
    def __init__(self, fisier, eurisitica):

        self.euristica_aleasa = eurisitica
        fin = open(fisier, "r");
        lines = fin.readlines()
        self.m = len(lines) // 2

        self.colors_matrix = lines[:self.m]
        self.artifacts_matrix = lines[self.m:]
        colors_matrix = self.colors_matrix
        artifacts_matrix = self.artifacts_matrix
        for i, line in enumerate(colors_matrix):
            colors_matrix[i] = colors_matrix[i].rstrip().split(' ')
        for i, line in enumerate(artifacts_matrix):
            artifacts_matrix[i] = artifacts_matrix[i].rstrip().split(' ')
        print(*colors_matrix, sep='\n')
        print(*artifacts_matrix, sep='\n')
        self.error = None
        l, c = np.where(np.array(artifacts_matrix) == '@')
        if len(l) == 0:
            fout = open(str("233_Stanimir_Andrei_6_output_" + fisier[-5] + ".txt"), "w")
            print("nu exista piatra")
            self.error = "nu exista piatra\n"
            return
        self.l_stone, self.c_stone = int(l), int(c)
        l, c = np.where(np.array(artifacts_matrix) == '*')
        if len(l) == 0:
            print("nu exista iesire")
            self.error("nu exista iesire\n")
            return
        self.l_exit, self.c_exit = int(l), int(c)

        self.n = len(colors_matrix[0])

        self.start_wizard = Wizard(int(l), int(c), colors_matrix[int(l)][int(c)], 2)

    def distanta(self, x, y, x2, y2):
        return abs(x - x2) + abs(y - y2)

    def calculeaza_distanta_scop(self, wizard: Wizard):
        if self.euristica_aleasa == 1:
            return self.euristica_1(wizard)
        else:
            return self.euristica_2(wizard)

    def euristica_1(self, wizard):
        # daca a gasit piatra, returneaza distanta manhattan de la piatra la iesire
        # functia este admisibila, pentru ca la fiecare pas, daca gasim papucii necesari,
        # drumul cel mai scurt catre destinatie este cel putin distanta manhattan.

        # Nu este consistenta, deoarece vrajitorul poate face pasi in directia opusa a iesirii,
        # astfel directia manhattan sa mareste fata de vrajitor in pozitia precedenta.
        if wizard.hasStone:
            return self.distanta(wizard.x, wizard.y, self.l_exit, self.c_exit)
        else:
            return inf;
        # return self.distanta(wizard.x, wizard.y, self.l_stone, self.c_stone) + \
        #       self.distanta(self.l_stone, self.c_stone, self.l_exit, self.c_exit)

    def euristica_2(self, wizard: Wizard):
        # verific daca poate ajunge la incaltaminte sau iesire inainte sa moara:
        # evit sa iau papuci care i-am mai luat
        # cand iau piatra, golesc lista wizard.prev_shoe_positions
        max_dist_possible = wizard.shoe_durability + wizard.reserve_durability
        min_dist = 9999
        for i in range(wizard.x - max_dist_possible, wizard.x + max_dist_possible + 1):
            for j in range(wizard.y - max_dist_possible, wizard.y + wizard.shoe_durability + 1):
                if 0 <= i < self.m and 0 <= j < self.n:
                    if self.artifacts_matrix[i][j].isalpha() and \
                            (i, j) not in wizard.prev_shoe_positions:
                        min_dist = min(self.distanta(i, j, wizard.x, wizard.y), min_dist)
        if min_dist == 9999:
            return 999999  # nu se poate progresa
        return self.euristica_1(wizard)

    def euristica_neadmisibila(self):
        # o posibila functie neadmisibila returneaza numarul de "patratele" neexplorate din pestera
        pass


class Problema:

    def __init__(self):
        self.n = 3
        self.nod_start = Nod([[2, 4, 3], [8, 7, 5], [1, 0, 6]], 0)  # Nod([[1,2,3],[4,5,6],[7,0,8]],0)#
        self.nod_scop = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

    def cauta_nod_nume(self, matrix):
        """Stiind doar informatia "info" a unui nod,
        trebuie sa returnati fie obiectul de tip Nod care are acea informatie,
        fie None, daca nu exista niciun nod cu acea informatie."""
        ### TO DO ... DONE
        for nod in self.noduri:
            if nod.matrix == matrix:
                return nod
        return None


""" Sfarsit definire problema """

""" Clase folosite in algoritmul A* """


class NodParcurgere:
    """O clasa care cuprinde informatiile asociate unui nod din listele open/closed
        Cuprinde o referinta catre nodul in sine (din graf)
        dar are ca proprietati si valorile specifice algoritmului A* (f si g).
        Se presupune ca h este proprietate a nodului din graf

    """
    cave = None  # atribut al clasei

    def __init__(self, nod_graf: Wizard, parinte=None, g=0, f=None):
        self.nod_graf = nod_graf  # obiect de tip Nod
        self.parinte = parinte  # obiect de tip Nod
        self.g = g  # costul drumului de la radacina pana la nodul curent
        if f is None:
            self.f = self.g + self.nod_graf.h
        else:
            self.f = f

    def drum_arbore(self):
        """
            Functie care calculeaza drumul asociat unui nod din arborele de cautare.
            Functia merge din parinte in parinte pana ajunge la radacina
        """
        nod_c = self
        drum = [nod_c]
        while nod_c.parinte is not None:
            drum = [nod_c.parinte] + drum
            nod_c = nod_c.parinte
        return drum

    def contine_in_drum(self, nod):
        """
            Functie care verifica daca nodul "nod" se afla in drumul dintre radacina si nodul curent (self).
            Verificarea se face mergand din parinte in parinte pana la radacina
            Se compara doar informatiile nodurilor (proprietatea info)
            Returnati True sau False.

            "nod" este obiect de tip Nod (are atributul "nod.info")
            "self" este obiect de tip NodParcurgere (are "self.nod_graf.info")
        """
        ### TO DO ... DONE
        nod_c = self
        while nod_c.parinte is not None:
            if nod == nod_c.nod_graf:
                return True
            nod_c = nod_c.parinte
        return False

    def expandeaza(self):
        # returneaza o lista de vrajitori noi, fiecare reprezinta un succesor
        l_succesori = []
        n = cave.n
        m = cave.m

        wizard = self.nod_graf
        wizards = []
        l, c = wizard.x, wizard.y
        if cave.artifacts_matrix[l][c].isalpha() and cave.artifacts_matrix[l][c] != '@':
            wizards = wizard.FoundShoes(cave.artifacts_matrix[l][c])
        elif cave.artifacts_matrix[l][c] == '@':
            wizard.hasStone = True
            wizard.action += "\nA gasit piatra\n"
            wizard.prev_shoe_positions = []
            wizards.append(wizard)
        if len(wizards) == 0:
            wizards.append(wizard)
        linie = [0, 0, 1, -1]
        coloana = [-1, 1, 0, 0]
        for i in range(len(wizards)):
            wizards[i].h = cave.calculeaza_distanta_scop(wizards[i])
        for wizard in wizards:
            for i in range(4):
                new_x, new_y = l + linie[i], c + coloana[i]
                if 0 <= new_x < m and 0 <= new_y < n:
                    # creez cate 2 vrajitori, unul care schimba papucii, iar celalat nu
                    if wizard.shoe_color == cave.colors_matrix[new_x][new_y]:  # don't swap shoes
                        new_wizard: Wizard = deepcopy(wizard)
                        # wizard.id = Wizard.id_counter
                        # Wizard.id_counter += 1
                        self.move_wizard(new_wizard, new_x, new_y)

                        l_succesori.append(new_wizard)
                    if wizard.reserve_color == cave.colors_matrix[new_x][new_y]:  # swap shoes
                        new_wizard: Wizard = deepcopy(wizard)
                        # wizard.id = Wizard.id_counter
                        # Wizard.id_counter += 1

                        new_wizard.shoe_color, new_wizard.reserve_color = new_wizard.reserve_color, new_wizard.shoe_color
                        new_wizard.shoe_durability, new_wizard.reserve_durability = new_wizard.reserve_durability, new_wizard.shoe_durability
                        new_wizard.action += "Isi schimba pantofii in culoarea: " + new_wizard.shoe_color + ". "
                        if new_wizard.reserve_durability > 0 and new_wizard.reserve_color.isalpha():
                            new_wizard.action += " Desaga " + new_wizard.shoe_color + " " + str(
                                3 - new_wizard.reserve_durability) + " purtari. "
                        self.move_wizard(new_wizard, new_x, new_y)

                        l_succesori.append(new_wizard)

        return l_succesori

    def move_wizard(self, new_wizard, new_x, new_y):
        # muta vrajitorul pe o pozitie noua
        new_wizard.action += "\n Pas " + str(new_wizard.nr_pas) + ") Se muta pe de pe {},{} pe {},{}.".format(
            new_wizard.x, new_wizard.y, new_x, new_y)
        new_wizard.nr_pas += 1
        new_wizard.x = new_x
        new_wizard.y = new_y
        new_wizard.shoe_durability -= 1
        if new_wizard.shoe_durability == 0:
            new_wizard.shoe_color = ''
        # new_wizard.id = Wizard.id_counter
        # Wizard.id_counter += 1
        new_wizard.action += "Incaltat: {} (purtari {})\n ".format(new_wizard.shoe_color,
                                                                   3 - new_wizard.shoe_durability)
        if new_wizard.reserve_durability > 0 and new_wizard.reserve_color.isalpha():
            new_wizard.action += " Desaga " + new_wizard.shoe_color + " " + str(
                3 - new_wizard.reserve_durability) + " purtari. "

        new_wizard.h = cave.calculeaza_distanta_scop(new_wizard)

    def test_scop(self, wizard):
        return wizard.hasStone and (wizard.x, wizard.y) == (self.cave.l_exit, self.cave.c_exit)

    def __str__(self):
        parinte = self.parinte if self.parinte is None else self.parinte.nod_graf
        return f"({self.nod_graf}, parinte={parinte}, f={self.f}, g={self.g})"


""" Algoritmul A* """


def str_info_noduri(l):
    """
        o functie folosita strict in afisari - poate fi modificata in functie de problema
    """
    sir = "["
    for x in l:
        sir += str(x) + "  "
    sir += "]"
    return sir


def afis_succesori_cost(l):
    """
        o functie folosita strict in afisari - poate fi modificata in functie de problema
    """
    sir = ""
    for (x, cost) in l:
        sir += "\nnod: " + str(x) + ", cost arc:" + str(cost)
    return sir


def in_lista(l, nod):
    """
        lista "l" contine obiecte de tip NodParcurgere
        "nod" este de tip Nod
    """
    for i in range(len(l)):
        if l[i].nod_graf == nod:
            return l[i]
    return None


def a_star():
    """
        Functia care implementeaza algoritmul A-star
    """
    rad_arbore = NodParcurgere(cave.start_wizard)
    Open = [rad_arbore]  # Open va contine elemente de tip NodParcurgere
    closed = []  # closed va contine elemente de tip NodParcurgere

    while len(Open) > 0:
        # print(str_info_noduri(Open))  # afisam lista Open
        nod_curent = Open.pop(0)  # scoatem primul element din lista Open
        closed.append(nod_curent)  # si il adaugam la finalul listei closed
        # print(nod_curent.nod_graf)
        # testez daca nodul extras din lista Open este nod scop (si daca da, ies din bucla while)
        if nod_curent.test_scop(nod_curent.nod_graf):
            nod_curent.nod_graf.action += "A iesit din pestera"
            break

        l_succesori = nod_curent.expandeaza()
        for nod_succesor in l_succesori:
            # "nod_curent" este tatal, "nod_succesor" este fiul curent
            cost_succesor = nod_succesor.h
            # daca fiul nu e in drumul dintre radacina si tatal sau (adica nu se creeaza un circuit)
            if (not nod_curent.contine_in_drum(nod_succesor)):

                # calculez valorile g si f pentru "nod_succesor" (fiul)
                g_succesor = nod_curent.g + cost_succesor  # g-ul tatalui + cost muchie(tata, fiu)
                f_succesor = g_succesor + nod_succesor.h  # g-ul fiului + h-ul fiului

                # verific daca "nod_succesor" se afla in closed
                # (si il si sterg, returnand nodul sters in nod_parcg_vechi
                nod_nou = None
                nod_parcg_vechi = in_lista(closed, nod_succesor)

                if nod_parcg_vechi is not None:  # "nod_succesor" e in closed
                    # daca f-ul calculat pentru drumul actual este mai bun (mai mic) decat
                    # 	   f-ul pentru drumul gasit anterior (f-ul nodului aflat in lista closed)
                    # atunci actualizez parintele, g si f
                    # si apoi voi adauga "nod_nou" in lista Open
                    if (f_succesor < nod_parcg_vechi.f):
                        closed.remove(nod_parcg_vechi)  # scot nodul din lista closed
                        nod_parcg_vechi.parinte = nod_curent  # actualizez parintele
                        nod_parcg_vechi.g = g_succesor  # actualizez g
                        nod_parcg_vechi.f = f_succesor  # actualizez f
                        nod_nou = nod_parcg_vechi  # setez "nod_nou", care va fi adaugat apoi in Open

                else:
                    # daca nu e in closed, verific daca "nod_succesor" se afla in Open
                    nod_parcg_vechi = in_lista(Open, nod_succesor)

                    if nod_parcg_vechi is not None:  # "nod_succesor" e in Open
                        # daca f-ul calculat pentru drumul actual este mai bun (mai mic) decat
                        # 	   f-ul pentru drumul gasit anterior (f-ul nodului aflat in lista Open)
                        # atunci scot nodul din lista Open
                        # 		(pentru ca modificarea valorilor f si g imi va strica sortarea listei Open)
                        # actualizez parintele, g si f
                        # si apoi voi adauga "nod_nou" in lista Open (la noua pozitie corecta in sortare)
                        if (f_succesor < nod_parcg_vechi.f):
                            Open.remove(nod_parcg_vechi)
                            nod_parcg_vechi.parinte = nod_curent
                            nod_parcg_vechi.g = g_succesor
                            nod_parcg_vechi.f = f_succesor
                            nod_nou = nod_parcg_vechi

                    else:  # cand "nod_succesor" nu e nici in closed, nici in Open
                        nod_nou = NodParcurgere(nod_graf=nod_succesor, parinte=nod_curent, g=g_succesor)
                    # se calculeaza f automat in constructor

                if nod_nou:
                    # inserare in lista sortata crescator dupa f
                    # (si pentru f-uri egale descrescator dupa g)
                    i = 0
                    while i < len(Open):
                        if Open[i].f < nod_nou.f:
                            i += 1
                        else:
                            while i < len(Open) and Open[i].f == nod_nou.f and Open[i].g > nod_nou.g:
                                i += 1
                            break

                    Open.insert(i, nod_nou)

    fout = open(str("233_Stanimir_Andrei_6_output_" + fisier[-5] + ".txt"), "a")
    print("\n------------------ Concluzie -----------------------")
    if len(Open) == 0:
        fout.write("\nLista open e vida, nu avem drum de la nodul start la nodul scop\n")
        # print("Lista open e vida, nu avem drum de la nodul start la nodul scop")
    else:
        print("Drum de cost minim: " + nod_curent.nod_graf.action)
        print("Nr mutari", len(nod_curent.drum_arbore()))
        fout.write("\nDrum de cost minim: " + nod_curent.nod_graf.action)
        fout.write("\nNr mutari: " + str(len(nod_curent.drum_arbore())))
    fout.close()


if __name__ == "__main__":
    fisiere = ["233_Stanimir_Andrei_6_input_1.txt", "233_Stanimir_Andrei_6_input_2.txt",
               "233_Stanimir_Andrei_6_input_3.txt", "233_Stanimir_Andrei_6_input_4.txt"]
    for fisier in fisiere:
        fout = open(str("233_Stanimir_Andrei_6_output_" + fisier[-5] + ".txt"), "w")
        fout.close()
    for fisier in fisiere:
        fout = open(str("233_Stanimir_Andrei_6_output_" + fisier[-5] + ".txt"), "a")
        for nr_euristica in [1, 2]:
            cave = Cave(fisier, nr_euristica)
            if cave.error is not None:
                fout.write(cave.error)
                break;
            NodParcurgere.cave = cave
            # Wizard.id_counter = 1
            t_inainte = ((time.time() * 1000))
            a_star()
            t_dupa = ((time.time() * 1000))
            print("Calculatorul a \"gandit\" timp de " + str(
                round(t_dupa - t_inainte, 2)) + " milisecunde cu euristica " + str(nr_euristica) + "\n")
            fout.write("Calculatorul a \"gandit\" timp de " + str(
                round(t_dupa - t_inainte, 2)) + " milisecunde cu euristica " + str(nr_euristica) + "\n")
        fout.close()
