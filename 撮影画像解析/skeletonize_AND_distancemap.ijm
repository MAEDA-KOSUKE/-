n=258;
PLACE="C:\\2019_11_30\\Image_data";
setBatchMode(true);
for(i=1;i<=n;i++){
	open(PLACE+"/binary/binary_"+i+".tif");

	
	for(j=0;j<=3;j++){
		selectWindow("binary_"+i+".tif");
		run("Duplicate...", "title=skeletonize_"+j*90+".tif");
		//run("Median...", "radius=2");				/*���f�B�A���t�B���^��ǉ�*/
		if(j!=3){
			run("Arbitrarily...", "angle="+90*j+" grid=1 interpolation=None fill");
			run("Skeletonize Oya");
			/* �??角度に戻�?*/
			run("Arbitrarily...", "angle="+ -90*j+"  grid=1 interpolation=None fill");
		}else{
			run("Rotate 90 Degrees Left");
			run("Skeletonize Oya");
			run("Rotate 90 Degrees Right");
		}
	}


	selectWindow("skeletonize_0.tif");
	saveAs("Tiff", PLACE+"/sk/sk_"+i+".tif");

	run("Analyze Particles...", "size=0-Infinity circularity=0-1 show=Masks display clear summarize");
	selectWindow("sk_"+i+".tif"); close();
	selectWindow("Mask of sk_"+i+".tif");
	saveAs("Tiff", PLACE+"/skeletonize/skeletonize_"+i+".tif");
	run("Duplicate...", "title=skeletonize_0.tif");
	
	skeletonizeANDALL2="skeletonize_0.tif";
	for(j=1;j<=3;j++){
		skeletonizeANDALL=skeletonizeANDALL2;
		imageCalculator("AND create", skeletonizeANDALL,"skeletonize_"+90*j+".tif");
		skeletonizeANDALL2=getTitle();
		selectWindow(skeletonizeANDALL); close();
		selectWindow("skeletonize_"+90*j+".tif"); close();
	}
	selectWindow(skeletonizeANDALL2);
	saveAs("Tiff",PLACE+"/tmp/skeletonizeANDALL.tif");
	run("Divide...", "value=255");	

	selectWindow("binary_"+i+".tif");
	run("Distance Map");	//Distance Map の作�?
	saveAs("Tiff",PLACE+"/tmp/distancemap.tif");
	run("Multiply...","value=2");
	
	selectWindow("skeletonize_"+i+".tif");
	run("Duplicate...","title=skeletonize_0.tif");
	selectWindow("skeletonize_"+i+".tif");	close();
	selectWindow("skeletonize_0.tif");
	run("Divide...","value=255");
	imageCalculator("Multiply create", "distancemap.tif","skeletonize_0.tif");
	selectWindow("distancemap.tif");	close();
	selectWindow("skeletonize_0.tif");	close();
	
	imageCalculator("Subtract create", "Result of distancemap.tif","skeletonizeANDALL.tif");

	//run("Image Calculator...", "image1=[Result of skeletonize_0] operationfiltered=Subtract image2=binarized.tif create");

	//保�?	selectWindow("Result of Result of distancemap.tif");
	saveAs("Tiff", PLACE+"/skeletonize_AND_distancemap30/skeletonize_AND_distancemap_"+i+".tif");	
	close();
	selectWindow("Result of distancemap.tif"); close();
	selectWindow("skeletonizeANDALL.tif"); close();
	print(i);
}
