DATA="C:\\2019_11_30\\Image_data\\"
n=258;
PLACE="C:\\2019_11_30\\read\\30\\"

setBatchMode(true);

for(i=70;i<=n-2;i++){
	open(DATA+"skeletonize_AND_distancemap30\\skeletonize_AND_distancemap_"+i+".tif");

	runMacro("CrossNumber.txt");
	close();
	
	selectWindow("Log");
	saveAs("Text", PLACE+"2019_11_30_"+i+".txt");
}
