import ROOT 
import sys


nm = sys.argv[1]
POI = sys.argv[2]


finn  = ROOT.TFile(nm)

tree = finn.Get("limit")

sig1 = 1
sig2 = 3.84 
bestfx = -99
prevx = -99
prevy = -99


cross1l = -99
cross1h = -99 
cross2l = -99
cross2h = -99


for iev,event in enumerate(tree): 
        
    xval = getattr(tree,POI)
    yval = 2*event.deltaNLL 
    if "war2" == POI : 
        xval = 4.1*xval
    
    if iev == 0: 
        bestfx = xval
    print yval,xval 
    
    if iev >=1 and (iev < tree.GetEntries() - 1 ) : 

        if (yval - sig1)*(prevy - sig1) < 0 : 
            print "1sig cross : ", yval, prevy
        
            #interpolation # 
            
            alpha = (yval - prevy)/( xval - prevx)
            beta  = yval - alpha*xval 

            cross = (sig1 - beta )/alpha
            print cross
            if cross > bestfx : 
                cross1h = cross
            else : 
                cross1l = cross
    
    
        if (yval - sig2)*(prevy - sig2) < 0 : 
            print "2sig cross : ", yval, prevy
        
            #interpolation # 
            
            alpha = (yval - prevy)/( xval - prevx)
            beta  = yval - alpha*xval 

            cross = (sig2 - beta )/alpha
            print cross
            
            if cross > bestfx : 
                cross2h = cross
            else : 
                cross2l = cross
    

    prevx = xval
    prevy = yval

#===== PRINT RESULT  ==============


print "Final result : "
plus  = 0
minus = 0
if not cross1h == -99 : 
    plus = cross1h - bestfx

if not cross1l == -99 : 
    minus = bestfx - cross1l
else : 
    minus = bestfx 

factor = 1 
if POI == "GGsm" : 
    factor = 4.1


print POI," = ",round(factor*bestfx,4),"^{+",round(factor*plus,4),"}_{-",round(factor*minus,4),"}  ,[",round(factor*cross2l,4)," , ",round(factor*cross2h,4),"]"


#=================================


