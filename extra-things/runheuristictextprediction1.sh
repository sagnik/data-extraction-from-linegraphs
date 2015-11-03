for file in pngs/colorfigures/training/*-mod.png; 
do 
 echo $file; 
 x=`basename $file`; 
 y=modjsons/${x:0:${#x}-4}.json; 
 echo $y;
 python heuristictextclassify4.py $y; 
done
#for file in pngs/colorfigures/training/*-mod.png ; 
#do 
# echo $file; 
# python producetextclassifiedimage.py $file; 
#done
#python convertodisplayhtmltextclassified.py
