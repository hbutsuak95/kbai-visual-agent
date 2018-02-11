from PIL import Image, ImageChops, ImageMath, ImageOps, ImageStat, ImageFilter
from ImageUtils import ImageUtils
import math, operator
from itertools import izip


class Agent:

    def __init__(self):
        pass

    imageUtils =ImageUtils()
    doNotGuess= 0
    def Solve(self, problem):

        print "problem name: " + problem.name

        if "Basic" not in problem.name:
            self.doNotGuess =1
        problem_figures = {}



        for figureName in problem.figures:
            figure = problem.figures[figureName]
            image = Image.open(figure.visualFilename).convert('1')

            problem_figures[figureName] = image
        strategy = self.chooseStrategy(problem_figures)

        if strategy == 'row_equals':
            for i in range(1, 9):
                if self.areEqual(problem_figures['H'], problem_figures[str(i)])[0]:
                   return int(i)
        elif strategy == 'one_of_each':
            return self.applyOnfOfEachStrategy(problem_figures)
        elif strategy == 'one_cancels':
            return self.applyOneCancelsStrategy(problem_figures)
        elif strategy == 'cancel_out':
            return self.applyCancelOutStrategy(problem_figures)
        elif strategy == 'common_perms':
            return self.applyCommonPermsStrategy(problem_figures)
        elif strategy == 'productAB':
            return self.applyProductABStrategy(problem_figures)
        elif strategy == 'productAC':
            return self.applyProductACStrategy(problem_figures)
        elif strategy == 'diffAB':
            return self.applyDiffABStrategy(problem_figures)
        elif strategy == 'shared':
            return self.applySharedStrategy(problem_figures)
        else:
            return self.pick_the_one_not_seen(problem_figures)

        return -1


    @staticmethod
    def areEqual(im1, im2):
        dif = sum(abs(p1 - p2) for p1, p2 in zip(im1.getdata(), im2.getdata()))

        ncomponents = im1.size[0] * im1.size[1] * 3
        dist = (dif / 255.0 * 100) / ncomponents
        im1__getcolors = im1.getcolors()
        im2_getcolors = im2.getcolors()
        black1 = (10000, 0)
        if len(im1__getcolors) > 1:
            black, white = im1__getcolors

        else:
            if im1__getcolors[0][1] == 255:
                white = im1__getcolors
                black = (0, 0)
            else:
                black = im1__getcolors
                white = (0, 255)

        if len(im2_getcolors) > 1:
            black1, white1 = im2_getcolors
        else:
            if im2_getcolors[0][1] == 255:
                white1 = im2_getcolors
                black1 = (0, 0)
            else:
                black1 = im2_getcolors
                white1 = (0, 255)



        stats = {"dist": dist, "blk": abs(black[0] - black1[0])}


        return (dist<1.1 and abs(black[0]-black1[0])<105), stats
        # return (dist<1.1 and abs(black[0]-black1[0])<105 and abs(white[0]-white1[0]<100)), stats

    def isShared(self, figures):
        sharedAB=self.imageUtils.compareImages(figures["A"], figures["B"])[0]
        sharedDE=self.imageUtils.compareImages(figures["D"], figures["E"])[0]
        return self.areEqual(sharedAB, figures["C"])[0] and self.areEqual(sharedDE, figures["F"])[0]

    def applySharedStrategy(self, figures):
        sharedGE=self.imageUtils.compareImages(figures["G"], figures["H"])[0]
        for i in range(1, 9):
            if self.areEqual(sharedGE, figures[str(i)])[0]:
                return int(i)
        else:
            return -1


    def chooseStrategy(self, figures):
        # everyone is the same
        figures_a_ = figures['A']
        figures_b_ = figures['B']
        figures_c_ = figures['C']
        figures_d_ = figures['D']
        figures_e_ = figures['E']
        figures_f_ = figures['F']
        figures_g_ = figures['G']
        figures_h_ = figures['H']

        # overlays
        rowAB = ImageChops.add(figures_a_, figures_b_)
        rowBC = ImageChops.add(figures_b_, figures_c_)
        rowDE = ImageChops.add(figures_d_, figures_e_)
        rowEF = ImageChops.add(figures_e_, figures_f_)


        colAD =ImageChops.multiply(figures_a_, figures_d_)
        colADG= ImageChops.multiply(colAD, figures_g_)

        colBE =ImageChops.multiply(figures_b_, figures_e_)
        colBEH= ImageChops.multiply(colBE, figures_h_)

        #common permutations
        ab = ImageChops.multiply(figures_a_,figures_b_)
        ac = ImageChops.multiply(figures_a_,figures_c_)
        df = ImageChops.multiply(figures_d_,figures_f_)
        abc = ImageChops.multiply(ab,figures_c_)
        de = ImageChops.multiply(figures_d_,figures_e_)
        de_F=ImageChops.multiply(de,figures_f_)

        #difs
        difAB=self.imageUtils.invertGrayScaleImage(ImageChops.difference(figures_a_, figures_b_))
        difDE=self.imageUtils.invertGrayScaleImage(ImageChops.difference(figures_d_, figures_e_))

        if self.areEqual(figures_a_, figures_b_)[0] and self.areEqual(figures_b_, figures_c_)[0]:
            if self.areEqual(figures_d_, figures_e_)[0] and self.areEqual(figures_e_, figures_f_)[0]:
                return 'row_equals'
        elif ((self.areEqual(figures_a_, figures_d_)[0] or self.areEqual(figures_a_, figures_e_)[0] or self.areEqual(figures_a_,figures_f_)[0]) \
                and (self.areEqual(figures_b_, figures_d_)[0] or self.areEqual(figures_b_, figures_e_)[0] or self.areEqual(figures_b_, figures_f_)[0]) \
                and (self.areEqual(figures_c_, figures_d_)[0] or self.areEqual(figures_c_, figures_e_)[0] or self.areEqual(figures_c_, figures_f_)[0])):

            return 'one_of_each'
        elif self.areEqual(rowAB, rowBC)[0] and self.areEqual(rowDE, rowEF)[0]:
            return "one_cancels"
        elif self.areEqual(colADG, colBEH)[0]:
            return "cancel_out"
        elif self.areEqual(ab, figures_c_)[0] and self.areEqual(de, figures_f_)[0] :
            return "productAB"
        elif self.areEqual(ac, figures_b_)[0] and self.areEqual(df, figures_e_)[0]:
            return "productAC"
        elif self.areEqual(difAB, figures_c_)[0] and self.areEqual(difDE, figures_f_)[0]:
            return "diffAB"
        elif self.isShared(figures):
            return "shared"
        elif self.areEqual(abc, de_F)[0]:
            return "common_perms"




    def applyOnfOfEachStrategy(self, problem_figures):
        if self.areEqual(problem_figures['A'], problem_figures['G'])[0] or self.areEqual(problem_figures['A'],problem_figures['H'])[0]:
            if self.areEqual(problem_figures['B'], problem_figures['G'])[0] or self.areEqual(problem_figures['B'],problem_figures['H'][0]):
                if self.areEqual(problem_figures['C'], problem_figures['G'])[0] or self.areEqual(problem_figures['C'],problem_figures['H'])[0]:
                    print  "need to chose another strategy"
                else:
                    missing_figure ='C'
            else:
                missing_figure ='B'
        else:
            missing_figure = "A"

        for i in range(1, 9):
            if self.areEqual(problem_figures[missing_figure], problem_figures[str(i)])[0]:
                return int(i)

    def applyOneCancelsStrategy(self, problem_figures):
        rowCF = ImageChops.add(problem_figures["C"], problem_figures["F"])
        rowGH = ImageChops.add(problem_figures["G"], problem_figures["H"])
        rowHF = ImageChops.multiply(problem_figures["H"], problem_figures["F"])
        answers ={}

        for i in range(1, 9):
            candidate = ImageChops.add(rowCF, problem_figures[str(i)])
            candidate2 = ImageChops.add(rowGH, problem_figures[str(i)])

            if self.areEqual(rowCF, candidate)[0] and self.areEqual(rowGH, candidate2)[0]:

                answers[i]= problem_figures[str(i)]

        if len(answers)!=1:
            if self.isShared(problem_figures):
                return self.applySharedStrategy(problem_figures)
            else:
                return self.pick_the_one_not_seen(problem_figures)
        else:
            return answers.keys()[0]


        return -1;


    def applyCommonPermsStrategy(self, figures):
        de = ImageChops.multiply(figures["D"],figures["E"])
        gh = ImageChops.multiply(figures["G"],figures["H"])
        de_F=ImageChops.multiply(de,figures["F"])



        for i in range (1,9):
            candidate= ImageChops.multiply(gh, figures[str(i)])
            if self.areEqual(candidate,de_F)[0]:
                return i
        return self.pick_the_one_not_seen(figures)

    def applyProductABStrategy(self, figures):
        gh = ImageChops.multiply(figures["G"],figures["H"])
        for i in range (1,9):
           if self.areEqual(gh,figures[str(i)])[0]:
                return i
        return self.pick_the_one_not_seen(figures)


    def applyProductACStrategy(self, figures):
        for i in range (1,9):
            candidate= ImageChops.multiply(figures["G"], figures[str(i)])
            if self.areEqual(candidate,figures["H"])[0]:
                return i
        return self.pick_the_one_not_seen(figures)

    def applyDiffABStrategy(self, figures):
        difGH=self.imageUtils.invertGrayScaleImage(ImageChops.difference(figures["H"], figures["G"]))
        for i in range (1,9):
            if self.areEqual(figures[str(i)],difGH)[0]:
                return i
        return self.pick_the_one_not_seen(figures)




    def pick_the_one_not_seen(self, figures):
        figs =["A","B","C","D","E","F","G", "H"]
        answers=[1,2,3,4,5,6,7,8]
        for fig in figs:
            for i in range(1,9):
                if self.areEqual(figures[fig], figures[str(i)])[0] :
                    if i in answers:
                        answers.remove(i)

        if len(answers)==1:
            return answers[0]
        elif self.doNotGuess:
            return -1
        return answers[0]

    def applyCancelOutStrategy(self,problem_figures):
         figures_a_ = problem_figures['A']
         figures_c_ = problem_figures['C']
         figures_d_ = problem_figures['D']
         figures_f_ = problem_figures['F']
         figures_g_ = problem_figures['G']

         colAD= ImageChops.multiply(figures_a_, figures_d_)
         colADG= ImageChops.multiply(colAD, figures_g_)
         colCF= ImageChops.multiply(figures_c_, figures_f_)

         for i in range(1, 9):
             candidate = ImageChops.multiply(colCF, problem_figures[str(i)])
             if self.areEqual(candidate,colADG)[0]:
                 return int(i)


         return -1

