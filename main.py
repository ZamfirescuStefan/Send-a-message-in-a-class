import os
from math import sqrt
import sys
import time


def citire_date(fin):
    lista_elevi = []
    elevi_suparati = []
    elevi_ascultati = []

    f = fin.readline()
    while f != "suparati:\n":
        lista_elevi.append(f[:-1].split(" "))
        f = fin.readline()

    f = fin.readline()
    while f != "ascultati:\n":
        elevi_suparati.append(f[:-1].split(" "))
        f = fin.readline()

    f = fin.readline()
    M = int(f.split(" ")[0])
    elevi_ascultati = [f[:-1].split(" ")[1]]
    f = fin.readline()
    while f.split(" ")[0] != "mesaj:":
        elevi_ascultati.append(f[:-1])
        f = fin.readline()

    emitator = f.split(" ")[1]
    receptor = f.split(" ")[3]
    # afisare_date(lista_elevi, elevi_suparati, elevi_ascultati, emitator, receptor)
    return lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor


def afisare_date(lista_elevi, elevi_suparati, elevi_ascultati, emitator, receptor):
    fout.write("Listele cu toti studentii ")
    for students in lista_elevi:
        fout.write(students)

    fout.write("Listele cu toti cei suparati")
    for elem in elevi_suparati:
        fout.write(elem)

    fout.write("Listele cu elevii ascultati")
    for elem in elevi_ascultati:
        fout.write(elem)

    fout.write("Emitatorul mesajului este {} iar receptorul este {} ".format(emitator, receptor))


""" 
    In program:
        -> x reprezinta linia 
        -> y reprezinta coloana 
"""


class NodParcurgere:
    graf = None  # static
    '''
     node info  => pozitia mesajului (x, y) pair 
                => pozitia profesorului (x, y) 
                => numele studentului (in nodParcurgere nu avem acces la lista de elevi)
                => directia din care a venit 
    '''

    def __init__(self, info, parinte, cost, h):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost  # costul de la radacina la nodul curent
        self.h = h
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self.info]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte.info)
            nod = nod.parinte
        return l

    def afisDrum(self):  # returneaza si lungimea drumului
        l = self.obtineDrum()
        outputString = str(l[0][2])
        for index in range(1, len(l)):
            outputString += l[index][3] + l[index][2]

        outputString += "\n"
        fout.write(outputString)
        fout.write(f"Lungime: {len(l)}\n")
        fout.write("Cost: {}".format(self.g))
        return len(l)

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            # pentru a vedea daca doua stari sunt la fel luam in
            # considerare doar pozitia biletului si a profesorului
            # nu si vecinul de la care a venit sau directia din care vine
            if infoNodNou[:-2] == nodDrum.info[:-2]:
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        return " bilet: {} {}, profesor: {} {}  f:{} \n".format(self.info[0][0], self.info[0][1], \
                                                                self.info[1][0], self.info[1][1], self.f)


class Graph:  # graful problemei
    def __init__(self, lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, tip_euristica):
        self.lista_elevi = lista_elevi
        self.elevi_suparati = elevi_suparati
        self.t_per_asculate = M
        self.elevi_ascultati = elevi_ascultati
        self.emitator = emitator
        self.receptor = receptor

        self.tip_euristica = tip_euristica
        #  lista de elevi pe care profesorul ii poate vedea daca trimite biletul
        self.elevi_inaccesibili = []

    def euristica_complexa (self, x, y):
        rand_nod_final, coloana_nod_final = self.find_elev(self.receptor)
        linia_optima = len(self.lista_elevi) - 1 if x == len(self.lista_elevi) - 1 else len(self.lista_elevi) - 2
        euristica_val = 0
        if (coloana_nod_final == y) or (y % 2 == 0 and coloana_nod_final == y + 1) or (y % 2 == 1 and coloana_nod_final == y - 1):
            euristica_val = abs(x - rand_nod_final)
        elif x == len(self.lista_elevi) - 1 and rand_nod_final == len(self.lista_elevi) - 1:
            euristica_val = abs(y - coloana_nod_final)
        else:
            euristica_val = abs(x - linia_optima) + abs(y - coloana_nod_final) + abs(x - linia_optima)

        # fout.write(f"Euristica de la elem {x}, {y} la nodul final este {euristica_val}\n")
        return  euristica_val

    def calculeaza_euristica(self, x, y):
        """
        calculeaza euristica pentru un nod pozitionat la coordonatele x, y
        :param x:
        :param y:
        :return: valoarea euristica in functie de tipul de euristica ales
        """
        if self.tip_euristica == 1:  # manhattan distance
            rand_nod_final, coloana_nod_final = self.find_elev(self.receptor)
            return abs(x - rand_nod_final) + abs(y - coloana_nod_final)
        elif self.tip_euristica == 2:  # euclidian distance
            return self.euristica_complexa(x, y)
        elif self.tip_euristica == 3:
            if x > len(self.lista_elevi) / 2:
                return x - 1  # euristica neadmisibila
            else:
                return x + 1
        else:
            if self.find_elev(self.receptor) != (x, y):
                return 1  # banal euristic
            else:
                return 0

    def testeaza_scop(self, nodCurent):
        return nodCurent.info[0] == self.find_elev(self.receptor)

    def genereazaSuccesori(self, nodCurent):
        listaSuccesori = []
        x_elev, y_elev = nodCurent.info[0]
        x_prof, y_prof = nodCurent.info[1][0]
        profesor_index = nodCurent.info[1][1]
        profesor_time = nodCurent.info[1][2]
        elevi_inaccesibili = []

        if x_prof != -1 and y_prof != -1:
            elevi_inaccesibili = self.profesor_list(x_prof, y_prof)
        new_x_prof, new_y_prof, new_prof_index, new_prof_time = self.next_pos_prof(x_prof, \
                                                                                   y_prof, \
                                                                                   profesor_index, \
                                                                                   profesor_time)
        info_prof = [(new_x_prof, new_y_prof), new_prof_index, new_prof_time]

        if x_elev > 0:
            vecin = self.lista_elevi[x_elev - 1][y_elev]
            afis_chr = " ^ "
            self.addToSucc(nodCurent, vecin, elevi_inaccesibili, info_prof, listaSuccesori, afis_chr)
        if x_elev < len(self.lista_elevi) - 1:
            vecin = self.lista_elevi[x_elev + 1][y_elev]
            afis_chr = " v "
            self.addToSucc(nodCurent, vecin, elevi_inaccesibili, info_prof, listaSuccesori, afis_chr)

        if y_elev % 2 == 0:
            vecin = self.lista_elevi[x_elev][y_elev + 1]
            afis_chr = " > "
            self.addToSucc(nodCurent, vecin, elevi_inaccesibili, info_prof, listaSuccesori, afis_chr)

            if x_elev >= len(self.lista_elevi) - 2 and y_elev > 0:
                vecin = self.lista_elevi[x_elev][y_elev - 1]
                afis_chr = " << "
                self.addToSucc(nodCurent, vecin, elevi_inaccesibili, info_prof, listaSuccesori, afis_chr)

        else:
            vecin = self.lista_elevi[x_elev][y_elev - 1]
            afis_chr = " < "
            self.addToSucc(nodCurent, vecin, elevi_inaccesibili, info_prof, listaSuccesori, afis_chr)

            if x_elev >= len(self.lista_elevi) - 2 and y_elev < len(self.lista_elevi[x_elev]) - 1:
                vecin = self.lista_elevi[x_elev][y_elev + 1]
                afis_chr = " >> "
                self.addToSucc(nodCurent, vecin, elevi_inaccesibili, info_prof, listaSuccesori, afis_chr)

        return listaSuccesori

    def addToSucc(self, nodCurent, vecin, elevi_inaccesibili, info_prof, listaSuccesori, afis_chr):
        """
        adauga elemente la lista de succesori si verifica daca acest nod pe care vreau sa l adaug este valid
        :param nodCurent:
        :param vecin:
        :param elevi_inaccesibili:
        :param info_prof:
        :param listaSuccesori:
        :param afis_chr:
        :return:
        """
        x_elev, y_elev = nodCurent.info[0]
        student_actual = self.lista_elevi[x_elev][y_elev]
        x, y = self.find_elev(vecin)
        nodeInformation = [(x, y), info_prof, vecin, afis_chr]
        if self.sunt_certati(student_actual, vecin) is False and vecin not in elevi_inaccesibili and \
                not nodCurent.contineInDrum(nodeInformation):

            cost = self.calculeaza_cost(nodCurent, vecin)
            # cost = nodCurent.g + 1
            h = self.calculeaza_euristica(x, y)
            nodNou = NodParcurgere(nodeInformation, nodCurent, cost, h)
            listaSuccesori.append(nodNou)

    def calculeaza_cost(self, nodCurent, vecin):
        cost = nodCurent.g
        x_nodCurent, y_nodCurent = nodCurent.info[0]
        x_vecin, y_vecin = self.find_elev(vecin)
        if (y_nodCurent % 2 == 0 and y_vecin == y_nodCurent - 1) or \
           (y_nodCurent % 2 == 1 and y_vecin == y_nodCurent + 1):
            cost += 2
        elif abs(x_nodCurent - x_vecin) == 1:
            cost += 1
        # fout.write(f"Costul de la {x_nodCurent}, {y_nodCurent} la {x_vecin}, {y_vecin} este {cost}\n")
        return cost

    def sunt_certati(self, nume_elev1, nume_elev2):
        """
        :param nume_elev1:
        :param nume_elev2:
        :return: returneaza true daca cei doi elevi sunt certati iar false in caz contrar
        """
        if nume_elev1 == "liber" or nume_elev2 == "liber":
            return True

        for nume in self.elevi_suparati:
            if nume[0] == nume_elev1 and nume[1] == nume_elev2 or \
                    nume[0] == nume_elev2 and nume[1] == nume_elev1:
                return True
        return False

    def find_elev(self, elev_name):
        """
        :param elev_name:
        :return: returneaza coordonatele din lista de elevi al acestuia, -1, -1 daca acesta nu exista in lista
        """
        for x in range(len(self.lista_elevi)):
            for y in range(len(self.lista_elevi[x])):
                if elev_name == self.lista_elevi[x][y]:
                    return x, y
        return -1, -1

    def next_pos_prof(self, x, y, profesor_index, profesor_time):
        """

        :param x:
        :param y:
        :param profesor_index: pe ce elev o sa asculte
        :param profesor_time: cat mai are de ascultat la elevul actual
        :return: returneaza urmatoarea pozitie a profesorului sau (-1, -1) daca nu mai exista
               elevi de ascultat
        """
        if profesor_time < self.t_per_asculate - 1:
            profesor_time += 1
            return x, y, profesor_index, profesor_time
        else:
            profesor_time = 0
            profesor_index += 1
            if profesor_index > len(self.elevi_ascultati) - 1:
                return -1, -1, -1, -1
            elev_name = self.elevi_ascultati[profesor_index]
            x, y = self.find_elev(elev_name)
            return [x, y, profesor_index, profesor_time]

    """
    primeste ca argumente pozitia profesorului si returneaza o lista cu elevi 
    la care nu putem sa trimitem biletul pentru ca il va vedea profesorul 
    """

    def profesor_list(self, x: int, y: int):
        """

        :param x: linia pe care se afla elevul pe care-l asculta
        :param y: coloana pe care se afla elevul pe care-l asculta
        :return: o lista de elevi la care nu putem sa trimitem mesajul in momentul actual
        """
        list_elevi = None
        list_elevi = [self.lista_elevi[x][y]]

        if x > 0:  # elevi de pe rand cu acel elev
            list_elevi.append(self.lista_elevi[x - 1][y])
        if x < len(self.lista_elevi) - 1:
            list_elevi.append(self.lista_elevi[x + 1][y])

        if y % 2 != 0:  # daca exista rand invecinat
            if y < len(self.lista_elevi[x]) - 1:
                list_elevi.append(self.lista_elevi[x][y + 1])
                if x > 0:
                    list_elevi.append(self.lista_elevi[x - 1][y + 1])
                if x < len(self.lista_elevi) - 1:
                    list_elevi.append(self.lista_elevi[x + 1][y + 1])
        else:
            if y > 0:
                list_elevi.append(self.lista_elevi[x][y - 1])
                if x > 0:
                    list_elevi.append(self.lista_elevi[x - 1][y - 1])
                if x < len(self.lista_elevi) - 1:
                    list_elevi.append(self.lista_elevi[x + 1][y - 1])
        return list_elevi

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return sir


def a_star_optimizat(gr, timeout):
    l_open = [NodParcurgere([gr.find_elev(gr.emitator), [gr.find_elev(gr.elevi_ascultati[0]), 0, 0], \
                               gr.emitator], None, 0, 1)]
    # l_closed contine nodurile expandate
    l_closed = []
    start_time = time.time()
    nr_max_noduri = 0
    nr_total_noduri = 0
    while len(l_open) > 0:
        nodCurent = l_open.pop(0)
        actual_time = time.time()
        l_closed.append(nodCurent)
        if timeout != -1:
            if actual_time - start_program_time >= timeout:
                fout.write("Limita de timp a fost deparita: \n")
                return
        if gr.testeaza_scop(nodCurent):
            fout.write("Solutie: ")
            nodCurent.afisDrum()
            fout.write("\nTimpul de gesire al solutiei: {}s\n".format(actual_time - start_time))
            fout.write(f"Numarul maxim de noduri la un moment dat este: {nr_max_noduri}\n")
            fout.write(f"Numarul total de noduri este: {nr_total_noduri}")
            fout.write("\n---------------------------------------------------------\n\n")
            return

        lSuccesori = gr.genereazaSuccesori(nodCurent)
        nr_total_noduri += len(lSuccesori)
        for s in lSuccesori:
            gasitC = False
            for nodC in l_open:
                if s.info == nodC.info:
                    gasitC = True
                    if s.f >= nodC.f:
                        lSuccesori.remove(s)
                    else:  # s.f<nodC.f
                        l_open.remove(nodC)
                    break
            if not gasitC:
                for nodC in l_closed:
                    if s.info == nodC.info:
                        if s.f >= nodC.f:
                            lSuccesori.remove(s)
                        else:  # s.f<nodC.f
                            l_closed.remove(nodC)
                        break
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(l_open)):
                if l_open[i].f > s.f or (l_open[i].f == s.f and l_open[i].g <= s.g):
                    gasit_loc = True
                    break
            if gasit_loc:
                l_open.insert(i, s)
            else:
                l_open.append(s)
        nr_max_noduri = max(nr_max_noduri, len(l_open))


def a_star(gr, nrSolutiiCautate, timeout):
    x, y = gr.find_elev(gr.emitator)
    nod_start = NodParcurgere([gr.find_elev(gr.emitator), [gr.find_elev(gr.elevi_ascultati[0]), 0, 0], \
                               gr.emitator], None, 0, 1)
    index_sol = 1
    c = [nod_start]
    start_time = time.time()
    nr_max_noduri = 0
    nr_total_noduri = 0
    while len(c) > 0:
        nodCurent = c.pop(0)
        actual_time = time.time()
        if timeout != -1:
            if actual_time - start_program_time >= timeout:
                fout.write("Limita de timp a fost deparita: \n\n")
                return

        if gr.testeaza_scop(nodCurent):
            global has_solution
            has_solution = True
            fout.write(f"Solutie {index_sol}: \n")
            nodCurent.afisDrum()
            fout.write("\nTimpul de gasire al solutiei: {}s\n".format(actual_time - start_time))
            fout.write(f"Numarul maxim de noduri la un moment dat este: {nr_max_noduri}\n")
            fout.write(f"Numarul total de noduri este: {nr_total_noduri}")
            fout.write("\n---------------------------------------------------------\n\n")
            nrSolutiiCautate -= 1
            index_sol += 1
            if nrSolutiiCautate == 0:
                return

        # fout.write(f"Nod curent {nodCurent.info[0]} are g = {nodCurent.g} si h = {nodCurent.h}\n")
        lSuccesori = gr.genereazaSuccesori(nodCurent)

        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                if c[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)
        nr_total_noduri += len(lSuccesori)
        nr_max_noduri = max(nr_max_noduri, len(c))


def ucs(gr, nrSolutiiCautate, timeout):
    nod_start = NodParcurgere([gr.find_elev(gr.emitator), [gr.find_elev(gr.elevi_ascultati[0]), 0, 0], \
                               gr.emitator], None, 0, 1)
    index_sol = 1
    c = [nod_start]
    start_time = time.time()
    nr_max_noduri = 0
    nr_total_noduri = 0
    while len(c) > 0:
        nodCurent = c.pop(0)
        acutual_time = time.time()
        if timeout != -1:
            if acutual_time - start_program_time >= timeout:
                fout.write("Limita de timp a fost deparita: \n")
                return
        if gr.testeaza_scop(nodCurent):
            global has_solution
            has_solution = True
            fout.write(f"Solutie {index_sol}: \n")
            nodCurent.afisDrum()
            fout.write("\nTimpul de gesire al solutiei: {}s\n".format(acutual_time - start_time))
            fout.write(f"Numarul maxim de noduri la un moment dat este: {nr_max_noduri}\n")
            fout.write(f"Numarul total de noduri este: {nr_total_noduri}")
            fout.write("\n---------------------------------------------------------\n\n")
            nrSolutiiCautate -= 1
            index_sol += 1
            if nrSolutiiCautate == 0:
                return

        lSuccesori = gr.genereazaSuccesori(nodCurent)

        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                if c[i].g >= s.g:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)

        nr_max_noduri = max(nr_max_noduri, len(c))
        nr_total_noduri += len(lSuccesori)


def ida_star(gr, nsol):
    nodStart = NodParcurgere([gr.find_elev(gr.emitator), [gr.find_elev(gr.elevi_ascultati[0]), 0, 0], \
                               gr.emitator], None, 0, 1)
    limita = nodStart.f
    actual_time = time.time()
    while True:

        # fout.write("Limita de pornire: " + str(limita))
        if timeout != -1:
            if actual_time - start_program_time >= timeout:
                fout.write("Limita de timp a fost deparita: \n")
                return

        nsol, rez = construieste_drum(gr, nodStart, limita, nsol)
        if rez == "gata":
            break
        if rez == float('inf'):
            # fout.write("Nu exista solutii!")
            break
        limita = rez
        # fout.write(">>> Limita noua: " + str(limita))


def construieste_drum(gr, nodCurent, limita, nsol):
    # fout.write("A ajuns la: " + str(nodCurent) + "\n")
    if nodCurent.f > limita:
        return nsol, nodCurent.f
    if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:
        fout.write("Solutie: \n")
        nodCurent.afisDrum()
        fout.write("\n----------------\n")
        nsol -= 1
        if nsol == 0:
            return 0, "gata"
    lSuccesori = gr.genereazaSuccesori(nodCurent)
    minim = float('inf')
    for s in lSuccesori:
        nsol, rez = construieste_drum(gr, s, limita, nsol)
        if rez == "gata":
            return 0, "gata"
        # fout.write("Compara " + str(rez) + " cu " + str(minim) + "\n")
        if rez < minim:
            minim = rez
            # fout.write("Noul minim: " + str(minim) + "\n")
    return nsol, minim


def check_args():
    """
    verifica daca argumentele primite de program sunt valide
    :return:
    """
    if len(sys.argv) != 5:
        print("Numar invalid de argumente, exiting...")
        sys.exit(0)
    else:
        try:
            dir_in = sys.argv[1]
            dir_out = sys.argv[2]
            nsol = int(sys.argv[3])
            timeout = int(sys.argv[4])
        except Exception as _:
            print("Argumentele au un tip gresit, exiting...")
            sys.exit(0)
    return dir_in, dir_out, nsol, timeout


def make_files(dir_in, dir_out):
    try:
        listaFisiere = os.listdir(dir_in)
    except Exception as _:
        print("Path to test4 file is invalid, exiting...")
        quit()
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)
    paths_out = []
    for numeFisier in listaFisiere:
        numeFisierOutput = f"{numeFisier}_out"
        f = open(f"{dir_out}/" + numeFisierOutput, "w")
        paths_out.append(f"{dir_out}/" + numeFisierOutput)
        f.close()
    for i in range(len(listaFisiere)):
        listaFisiere[i] = dir_in + "/" + listaFisiere[i]
    return listaFisiere, paths_out


def check_input(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor):
    is_emitator_exists = False
    is_receptor_exists = False
    for index in range(len(lista_elevi)):
        for index2 in range(len(lista_elevi[index])):
            if lista_elevi[index][index2] == emitator:
                is_emitator_exists = True
            if lista_elevi[index][index2] == receptor:
                is_receptor_exists = True

    if is_emitator_exists is False or is_receptor_exists is False:
        fout.write("Emitatorul sau repectorul nu exita, verificati inputul sau " +
                   "unul din acesti colegi lipsesc ")
        return


def main():
    global timeout
    dir_in, dir_out, nsol, timeout = check_args()
    input_files, output_files = make_files(dir_in, dir_out)

    # tip_euristica = int(input("Alege tipurl de euristica: \n" +
    #                           "1) Manhatten \n" +
    #                           "2) Euristica complexa \n" +
    #                           "3) Neadmisibila \n" +
    #                           "4) Banala \n"))

    for index in range(len(input_files)):
        fin = open(input_files[index], 'r')
        output_file = output_files[index]
        global fout
        fout = open(output_file, "w")

        lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor = citire_date(fin)
        check_input(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor)
        gr = Graph(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, 2)

        global has_solution
        has_solution = False
        # daca timeout-ul este -1 programul se va rula fara timeout
        fout.write("          ----- A star euristica 1 -----\n")
        gr = Graph(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, 1)
        global start_program_time

        start_program_time = time.time()
        a_star(gr, nsol, timeout)

        fout.write("\n          ----- A star euristica 2 -----\n")
        gr = Graph(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, 2)
        start_program_time = time.time()
        a_star(gr, nsol, timeout)

        fout.write("\n          ----- A star euristica neadmisibila -----\n")
        gr = Graph(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, 3)
        start_program_time = time.time()
        a_star(gr, nsol, timeout)

        fout.write("\n          ----- A star euristica banala -----\n")
        gr = Graph(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, 4)
        start_program_time = time.time()
        a_star(gr, nsol, timeout)

        fout.write("\n          ----- A star optimizat euristica 1 -----\n")
        start_program_time = time.time()
        gr = Graph(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, 1)
        a_star_optimizat(gr, timeout)

        fout.write("\n          ----- A star optimizat euristica 2-----\n")
        start_program_time = time.time()
        gr = Graph(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, 2)
        a_star_optimizat(gr, timeout)

        fout.write("\n          ----- A star optimizat euristica neadmisibila-----\n")
        start_program_time = time.time()
        gr = Graph(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, 3)
        a_star_optimizat(gr, timeout)

        fout.write("\n          ----- A star optimizat euristica banala -----\n")
        start_program_time = time.time()
        gr = Graph(lista_elevi, elevi_suparati, M, elevi_ascultati, emitator, receptor, 4)
        a_star_optimizat(gr, timeout)

        fout.write("\n          ----- UCS -----\n")
        start_program_time = time.time()
        ucs(gr, nsol, timeout)

        fout.write("\n          ----- IDA star -----\n")
        ida_star(gr, nsol)

        if has_solution is False:
            fout.write("This input has no solutions .... :(")
        fin.close()
        fout.close()


if __name__ == '__main__':
    main()
