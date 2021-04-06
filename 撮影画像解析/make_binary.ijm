n=258;
PLACE="C:\\2019_11_30\\image_data";
setBatchMode(true);

for(i=1;i<=n-2;i++){
	open(PLACE+"/SB_original/SB_original_"+i+".tif");
	
	run("Duplicate...","title=SB_original_"+i+"-1.tif");
	run("Mean...","radius=20");
	selectWindow("SB_original_"+i+".tif");
	run("Duplicate...","title=SB_original_"+i+"-2.tif");
	run("Mean...","radius=5");

	imageCalculator("Subtract create","SB_original_"+i+".tif","SB_original_"+i+"-1.tif");
	saveAs("Tiff",PLACE+"/tmp/mean_a.tif");
	selectWindow("SB_original_"+i+"-1.tif"); close();
	
	imageCalculator("Subtract create","SB_original_"+i+".tif","SB_original_"+i+"-2.tif");
	saveAs("Tiff",PLACE+"/tmp/mean_b.tif");
	selectWindow("SB_original_"+i+"-2.tif"); close();
	
	imageCalculator("Add create","mean_a.tif","mean_b.tif");
	selectWindow("mean_a.tif"); close();
	selectWindow("mean_b.tif"); close();
	selectWindow("SB_original_"+i+".tif"); close();
	
	selectWindow("Result of mean_a.tif");
	saveAs("Tiff",PLACE+"/tmp/Result of mean_a"+i+".tif");
	run("8-bit");
	setThreshold(1, 11);
	run("Convert to Mask");
	run("Analyze Particles...", "size=100-Infinity circularity=0.00-0.2 show=Masks display clear summarize");
	run("Close-");
	saveAs("Tiff",PLACE+"/binary/binary_"+i+".tif"); close();
	selectWindow("Result of mean_a"+i+".tif"); close();
	
	print("binarize...No."+i+"/"+n+"finished!");
}

print("complete!!");
