#!/usr/bin/env python
from array import array
from glob import glob
from itertools import izip
import math
import numpy as np
import os
import pipes
import random
import shutil
import subprocess
import sys

import ROOT

from helper_functions import replaceByMap

ROOT.gROOT.SetBatch(True)



#from Alignment.OfflineValidation.TkAlAllInOneTool.helperFunctions import replaceByMap

from plotlimits_standalone import drawlines
import stylefunctions as style
from utilities import cache, cd, deprecate, mkdir_p, mkdtemp, PlotCopier, TFile

class Folder(object):
    def __init__(self, folder, title, color, analysis, subdir, plotname, graphnumber=None, repmap=None, linestyle=None, linewidth=None, secondcolumn=None, removepoints=None, forcepoints=None, transformx=lambda x: x):
        if removepoints is None: removepoints = []
        if forcepoints is None: forcepoints = {}
        self.__folder, self.__title, self.color, self.analysis, self.subdir, self.plotname, self.graphnumber, self.linestyle, self.linewidth, self.secondcolumn, self.removepoints, self.forcepoints, self.transformx = folder, title, color, analysis, subdir, plotname, graphnumber, linestyle, linewidth, secondcolumn, removepoints, forcepoints, transformx
        self.repmap = {
                       "analysis": str(self.analysis),
                      }
        if repmap is not None: self.repmap.update(repmap)
    @property
    def folder(self):
        result = os.path.join(replaceByMap(self.__folder, self.repmap))
        gl = glob(result)
        if not gl:
            raise ValueError("{} does not exist!".format(result))
        if len(gl) > 1:
            raise ValueError("{} returns more than one match!".format(result))
        return gl[0]
    @property
    def title(self):
        return replaceByMap(self.__title, self.repmap)
    @title.setter
    def title(self, newtitle):
        self.__title = newtitle
    @property
    @cache
    def graph(self):
        with TFile(replaceByMap(os.path.join(self.folder, self.plotname), self.repmap)) as f:
            c = f.c1
            mg = c.GetListOfPrimitives()[1]
            graphs = mg.GetListOfGraphs()
            graphnumber = self.graphnumber
            if self.graphnumber is None:
                assert len(graphs) == 1
                graphnumber = 0
            self.__xtitle = mg.GetXaxis().GetTitle()
            self.__ytitle = mg.GetYaxis().GetTitle()
            g = graphs[graphnumber]
            n = g.GetN()
            x = np.array([g.GetX()[i] for i in xrange(n) if not any(np.isclose(g.GetX()[i], _) for _ in self.removepoints)])
            y = np.array([g.GetY()[i] for i in xrange(n) if not any(np.isclose(g.GetX()[i], _) for _ in self.removepoints)])
            for forcex, forcey in self.forcepoints.iteritems():
                forceindices = np.isclose(x, forcex)
                assert sum(forceindices) == 1, forceindices
                print (y[forceindices], forcey)
                y[forceindices] = forcey
                print (y[forceindices])
            x = np.array([self.transformx(_) for _ in x])
            y -= min(y)
            newg = ROOT.TGraph(len(x), x, y)
            newg.SetLineColor(self.color)
            if self.linestyle is not None:
                newg.SetLineStyle(self.linestyle)
            if self.linewidth is not None:
                newg.SetLineWidth(self.linewidth)
            return newg
    @property
    def xtitle(self):
        self.graph
        return self.__xtitle
    @property
    def ytitle(self):
        self.graph
        return self.__ytitle
    def addtolegend(self, legend, graph=None):
        if graph is None: graph = self.graph
        legend.AddEntry(self.graph, self.title, "l")
        if self.secondcolumn is not None:
            legend.AddEntry(0, self.secondcolumn, "")

analyses = "fa3", "fa2", "fL1", "fL1Zg"
setmax = 1
def getplotname(analysis, comparecategories):
    return "plot6D_{}.root".format(analysis)

def applystyle(mgs, mglogs, folders, xboundaries, xdivides, ydivide):
    assert len(mgs) == len(mglogs) == len(xdivides)+1
    for mg, mglog, xmin, xmax, fractionxmin, fractionxmax in zip(mgs, mglogs, [-setmax]+list(xdivides), list(xdivides)+[setmax], xboundaries[:-1], xboundaries[1:]):
        mglog.GetXaxis().SetLimits(xmin, xmax)
        mglog.GetXaxis().CenterTitle()
        mglog.GetYaxis().CenterTitle()
        mglog.SetMinimum(ydivide)
        #mglog.SetMaximum(250)
        style.applyaxesstyle(mglog)
        mglog.GetXaxis().SetLabelOffset(9999999)
        mglog.GetXaxis().SetTitleOffset(9999999)
        mglog.GetYaxis().SetLabelSize(.1)
        mglog.GetYaxis().SetTitleSize(.1)

        mg.GetXaxis().SetLimits(xmin, xmax)
        mg.GetXaxis().CenterTitle()
        mg.GetYaxis().CenterTitle()
        mg.SetMinimum(0)
        mg.SetMaximum(ydivide)
        style.applyaxesstyle(mg)
        mg.GetXaxis().SetLabelSize(.1 / (3*(fractionxmax - fractionxmin)))
        mg.GetXaxis().SetTitleOffset(.6)
        mg.GetYaxis().SetLabelSize(.1 / (3*(fractionxmax - fractionxmin)))
        mg.GetXaxis().SetTitleSize(.15 / (3*(fractionxmax - fractionxmin)))
        mg.GetYaxis().SetTitleSize(.1 / (3*(fractionxmax - fractionxmin)))
        mg.GetXaxis().SetLabelOffset(-0.0165)

    mgs[0].GetXaxis().SetLabelOffset(0.007)
    mgs[-1].GetXaxis().SetLabelOffset(-0.012)

    mgs[len(mgs)/2].GetXaxis().SetTitle(folders[0].xtitle)
    for mg, mglog in izip(mgs[1:], mglogs[1:]):
        mglog.GetYaxis().SetLabelOffset(9999999)
        mglog.GetYaxis().SetTitleOffset(9999999)
        mg.GetYaxis().SetLabelOffset(9999999)
        mg.GetYaxis().SetTitleOffset(9999999)

def PRL_loglinear(**kwargs):
    commondrawlineskwargs = {
                             "logscale": False,  #the lines are in the linear part
                             "xsize": .2,
                             "ysize": .045,
                             "yshift68": .03,
                             "yshift95": .03,
                            }

    markerposition = kwargs.pop("markerposition", None)
    onlyanalysis = kwargs.pop("analysis", None)
    xdivides = sorted(float(_) for _ in kwargs.pop("xdivides", (-.03, .03)))
    assert len(xdivides) == 2, xdivides
    ydivide = float(kwargs.pop("ydivide", 11))
    saveas = kwargs.pop("saveas", None)
    comparecategories = bool(int(kwargs.pop("comparecategories", False)))

    commondrawlineskwargs.update(kwargs)

    saveasdir = "."

    for k, v in commondrawlineskwargs.items():
        if k == "xpostext":
            try:
                commondrawlineskwargs[k] = float(v)
            except ValueError:
                pass
        elif k in ("xmin", "xmax"):
            commondrawlineskwargs[k] = float(v)

    for i, (analysis, letter) in reversed(list(enumerate(izip(analyses, "abcd"), start=1))):
        if analysis != onlyanalysis is not None: continue
        if analysis == "fa3":
            CLtextposition=.65
        elif analysis == "fa2":
            CLtextposition=-.8
        elif analysis == "fL1":
            CLtextposition=.65
        elif analysis == "fL1Zg":
            CLtextposition=-.8
        else:
            assert False

        c = plotcopier.TCanvas("c{}".format(random.randint(1, 1000000)), "", 8, 30, 1600, 1600)

        leftmargin = .1
        rightmargin = .02 #apply to the individual pads or 1 of the x axis gets cut off
        topmargin = .07
        bottommargin = .12
        biglegend = True
        #assert abs((leftmargin + rightmargin) - (topmargin + bottommargin)) < 1e-5, (leftmargin + rightmargin, topmargin + bottommargin)
        c.SetLeftMargin(0)
        c.SetRightMargin(0)
        c.SetTopMargin(0)
        c.SetBottomMargin(0)
        xboundaries = [0, leftmargin+(1-leftmargin-rightmargin)/3, leftmargin+(1-leftmargin-rightmargin)*2/3, 1]
        yboundaries = [0, bottommargin+(1-bottommargin-topmargin)/2, 1]
        if biglegend:
            if analysis == "fa2":
                legendposition = .4, .57, .8, .87
            elif analysis == "fL1":
                legendposition = .2, .57, .6, .87
            else:
                legendposition = .3, .57, .7, .87
        else:
            legendposition = 0, .2, 1, .8*(1-topmargin)
        logpads = [
          ROOT.TPad(c.GetName()+"_1", "_1", xboundaries[0], yboundaries[1], xboundaries[1], yboundaries[2]),
          ROOT.TPad(c.GetName()+"_2", "_2", xboundaries[1], yboundaries[1], xboundaries[2], yboundaries[2]),
          ROOT.TPad(c.GetName()+"_3", "_3", xboundaries[2], yboundaries[1], xboundaries[3], yboundaries[2]),
        ]
        linearpads = [
          ROOT.TPad(c.GetName()+"_4", "_4", xboundaries[0], yboundaries[0], xboundaries[1], yboundaries[1]),
          ROOT.TPad(c.GetName()+"_5", "_5", xboundaries[1], yboundaries[0], xboundaries[2], yboundaries[1]),
          ROOT.TPad(c.GetName()+"_6", "_6", xboundaries[2], yboundaries[0], xboundaries[3], yboundaries[1]),
        ]
        legendpad = logpads[1]
        for _ in linearpads + logpads:
            _.Draw()
            _.SetTicks()
            _.SetLeftMargin(0)
            _.SetRightMargin(0)
            _.SetTopMargin(0)
            _.SetBottomMargin(0)
        logpads[-1].SetRightMargin(rightmargin*len(logpads))

        repmap = {"analysis": str(analysis)}
        subdir = ""

        folders = [
            Folder("./", "Expected", 2, analysis, subdir, plotname="scan_test_new.root", graphnumber=0, repmap=repmap, linestyle=1, linewidth=2),
            #Folder("./", "STXS (stage-1)", 4, analysis, subdir, plotname="output_fa3gg.root", graphnumber=1, repmap=repmap, linestyle=7, linewidth=2),
            #Folder("./", "production", 4, analysis, subdir, plotname="output_fa3gg.root", graphnumber=1, repmap=repmap, linestyle=1, linewidth=2),
          
          
        ]

        #

        mg = ROOT.TMultiGraph("limit", "")
        for folder in folders:
            mg.Add(folder.graph)

        drawlineskwargs = commondrawlineskwargs.copy()
        drawlineskwargs["xpostext"] = CLtextposition

        CLpadindex = 0
        for _ in xdivides:
          if CLtextposition > _:
            CLpadindex += 1
        drawlineskwargs["textsize"] = (
          0.09 / (3*(xboundaries[CLpadindex+1] - xboundaries[CLpadindex]))
        )

        if markerposition:
            markerposition = [array('d', [_]) for _ in markerposition]
            marker = ROOT.TGraph(1, *markerposition)
            marker.SetMarkerStyle(20)
            marker.SetMarkerColor(4)
            marker.SetMarkerSize(3)
            if marker.GetY()[0] > 0:
                mg.Add(marker, "P")
        mglog = mg.Clone(mg.GetName()+"_log")
        if markerposition and marker.GetY()[0] <= 0:
            mg.Add(marker, "P")
        mgs = [mg, mg.Clone(mg.GetName()+"_1"), mg.Clone(mg.GetName()+"_2")]
        mglogs = [mglog, mglog.Clone(mglog.GetName()+"_1"), mglog.Clone(mglog.GetName()+"_2")]
        for logpad, mglog in izip(logpads, mglogs):
            logpad.cd()
            logpad.SetLogy()
            mglog.Draw("al")
            logpad.SetTopMargin(topmargin*2)
        logpads[-1].SetRightMargin(rightmargin * 1 / (xboundaries[-1] - xboundaries[-2]))
        logpads[0].SetLeftMargin(leftmargin * 1 / (xboundaries[1] - xboundaries[0]))
        c.cd()
#        style.subfig(letter, textsize=.04, x1=.91, x2=.94, y1=.88, y2=.92)

        for i, (linearpad, mg) in enumerate(izip(linearpads, mgs)):
            linearpad.cd()
            mg.Draw("al")
            linearpad.SetBottomMargin(bottommargin*2)

        linearpads[-1].SetRightMargin(rightmargin * 1 / (xboundaries[-1] - xboundaries[-2]))
        linearpads[0].SetLeftMargin(leftmargin * 1 / (xboundaries[1] - xboundaries[0]))

        applystyle(mgs, mglogs, folders, xboundaries, xdivides, ydivide)

        for i, (linearpad, mg) in enumerate(izip(linearpads, mgs)):
            linearpad.cd()
            paddrawlineskwargs = drawlineskwargs.copy()
            if i != CLpadindex: paddrawlineskwargs["yshift68"] = paddrawlineskwargs["yshift95"] = 100
            drawlines(**paddrawlineskwargs)

        (c if biglegend else legendpad).cd()
        l = ROOT.TLegend(*legendposition)
        l.SetBorderSize(0)
        l.SetFillStyle(0)
        for folder in folders:
            folder.addtolegend(l)
        if any(folder.secondcolumn is not None for folder in folders):
            assert all(folder.secondcolumn is not None for folder in folders)
            legend.SetNColumns(2)
        l.SetTextSize(.04 if biglegend else .1)
        l.Draw()
        c.cd()
        style.applycanvasstyle(c)
        style.CMS("", lumi=None, lumitext="",
                      x1=0.007, x2=1.01, #???
                      drawCMS=False, extratextsize=.039)
        style.CMS("",lumi=138, lumitext=None, x1=0.08, x2=1.025, y1=.95, y2=1, CMStextsize=.06, extratextsize=.039,drawCMS=True)
        yaxislabel(folders[0].ytitle).Draw()

        mkdir_p(os.path.join(saveasdir, "preliminary"))
        mkdir_p(os.path.join(saveasdir, "workinprogress"))
        plotname = getplotname(analysis, comparecategories)
        assert ".root" in plotname
        print (plotname)
        #saveas = "test.png"
        if saveas is not None:
            c.SaveAs(saveas)
        else:
            for ext in "png eps root pdf".split():
                c.SaveAs(os.path.join(saveasdir, replaceByMap(plotname.replace("root", ext), repmap)))

                #tt = plotname.replace("root",ext)
                #print "this",ext,remap
                #tt = replaceByMap(plotname.replace("root", ext), remap)
                #print tt
                #namename = os.path.join(saveasdir, tt)   #replaceByMap(plotname.replace("root", ext), repmap))

                #print (tt,namename)
                #c.SaveAs(str(namename))
                #print ("here")
            with plotcopier.open(os.path.join(saveasdir, replaceByMap(plotname.replace("root", "txt"), repmap)), "w") as f:
                f.write(" ".join(["python"]+[pipes.quote(_) for _ in sys.argv]))
                f.write("\n\n\n\n\n\ngit info:\n\n")
                f.write(subprocess.check_output(["git", "rev-parse", "HEAD"]))
                f.write("\n")
                f.write(subprocess.check_output(["git", "status"]))
                f.write("\n")
                f.write(subprocess.check_output(["git", "diff"]))

        style.CMS("", x1=0.12, x2=1.025, y1=.93, y2=1, drawCMS=True, CMStextsize=.06, extratextsize=.039)

        if saveas is not None:
            assert False
        else:
            for ext in "png eps root pdf".split():
                c.SaveAs(os.path.join(saveasdir, "preliminary", replaceByMap(plotname.replace("root", ext), repmap)))
            with plotcopier.open(os.path.join(saveasdir, "preliminary", replaceByMap(plotname.replace("root", "txt"), repmap)), "w") as f:
                f.write(" ".join(["python"]+[pipes.quote(_) for _ in sys.argv]))
                f.write("\n\n\n\n\n\ngit info:\n\n")
                f.write(subprocess.check_output(["git", "rev-parse", "HEAD"]))
                f.write("\n")
                f.write(subprocess.check_output(["git", "status"]))
                f.write("\n")
                f.write(subprocess.check_output(["git", "diff"]))

        del c.GetListOfPrimitives()[-1]  #delete Preliminary
        style.CMS("Work in progress", x1=0.12, x2=1.025, y1=.85, y2=.93, drawCMS=True, CMStextsize=.06, extratextsize=.039)

        if saveas is not None:
            assert False
        else:
            for ext in "png eps root pdf".split():
                c.SaveAs(os.path.join(saveasdir, "workinprogress", replaceByMap(plotname.replace("root", ext), repmap)))
            with plotcopier.open(os.path.join(saveasdir, "workinprogress", replaceByMap(plotname.replace("root", "txt"), repmap)), "w") as f:
                f.write(" ".join(["python"]+[pipes.quote(_) for _ in sys.argv]))
                f.write("\n\n\n\n\n\ngit info:\n\n")
                f.write(subprocess.check_output(["git", "rev-parse", "HEAD"]))
                f.write("\n")
                f.write(subprocess.check_output(["git", "status"]))
                f.write("\n")
                f.write(subprocess.check_output(["git", "diff"]))

@cache
def yaxislabel(label, textsize=.06):
    pt = ROOT.TPaveText(.01, 0, .03, 1, "brNDC")
    pt.SetBorderSize(0)
    pt.SetFillStyle(0)
    pt.SetTextAlign(22)
    pt.SetTextFont(42)
    pt.SetTextSize(.2)
    text = pt.AddText(.5,.5,label)
    text.SetTextSize(textsize)
    text.SetTextAngle(90)
    return pt

if __name__ == "__main__":
    import argparse

    def f(x): result = x.split("="); assert len(result)==2, x; return result

    p = argparse.ArgumentParser()
    p.add_argument("kwargs", type=f, nargs="*")
    p.add_argument("--analysis", choices="fa3 fa2 fL1 fL1Zg".split())
    args = p.parse_args()

    kwargs = {k: v for k, v in args.kwargs}
    if "analysis" in kwargs: args.analysis = kwargs["analysis"]

    function = PRL_loglinear
    with PlotCopier() as plotcopier:
        for kwargs["analysis"] in "fa3", "fa2", "fL1", "fL1Zg":
            if kwargs["analysis"] != args.analysis is not None: continue
            function(**kwargs)
