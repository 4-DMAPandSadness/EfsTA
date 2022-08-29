# **Evaluation of femtosecond Transient Absorption spectroscopy (EfsTA)**
> Plotting and fitting of TA-data for the Decay Associated Spectra (DAS) and the Species Associated Spectra (SAS) with a matrix reconstruction algorithm. The Global Lifetime Analysis (GLA) and the Global Target Analysis (GTA) are being applied.

This TA-Evaluation programm most importantly allows the optimizing of the decay constants based on the values given. These values should be derived of the 2D-data and previous knowledge of the photophysics of the molecule.

Also the original and the fitted data can be plotted in a beautiful 3-in-1-image as the one seen below.

![](3-in-1-SAS.png)

You can decide between using the grafical user-interface *EfsTA.exe* or the script form *App.py* in Python. They both have the features for the evaluation (GLA -> DAS and GTA -> SAS), as well as the plotting. However the UI checks for the completeness of the user inputs, whereas the script allows more customization.

## GUI

Upon starting the programm by double clicking the file a window in dark mode will pop up. On the top you can select your data, on the left you can choose the images you wish to plot and on the right you have to decide between SAS and DAS. The inputs you write will be cached for later use.

<img src="gui_start.png" width="50%"/>

### Select your folder

First, you can choose the `"folder/"` where the files of your TA-data reside on the top of the window.

Files with the following names will be recognized:
> `"folder/...lambda.txt"` contains the wavelengths/nm,  
> `"folder/...delays.txt"` contains the delays/ps,  
> `"folder/...spectra.txt"` contains the absorption change.

### Select the plots

On the left side of the window, you can decide which images will be plotted.

<img src="/pictures/gui_plot.png" width="30%"/>

You can choose between the original and/or the fitted data. The following options are available for the plots:

- *ΔA/λ*: chosen delay values will be plotted in a plot of the absorption change against the wavelenghts

<img src="/pictures/plot3.png" width="30%"/>

- *t/ΔA*: chosen wavelength values will be plotted in a plot of the delays against the absorption change

<img src="/pictures/plot1.png" width="30%"/>

- *2D heatmap*: the absorption change will be plotted as a heatmap of the delays against the wavelenghts

<img src="/pictures/plot2.png" width="50%"/>

- *all in one*: this is an image of the three plots mentioned above combined

<img src="/pictures/3-in-1.png" width="70%"/>

- *kinetics c/t*: the concentration of all species will be plotted against the delays

<img src="/pictures/kinetics.png" width="35%"/>

- *associated spectra (ΔA/λ)*: the DAS or SAS in a plot of the absorption change against the delays

<img src="/pictures/SAS.png" width="35%"/>

- *residuals*: saves an 1D plot of the residuals (from SAS or DAS) against the delays and a heatmap of the residuals

<img src="/pictures/res_1D.png" width="35%"/>
<img src="/pictures/res_2D.png" width="50%"/>

### Settings for the plots

If you wish to customize your plots, you can push the button *Next*.

<img src="/pictures/gui_plot_det.png" width="30%"/>

There you will be offered with the following possibilities:

- *specific delays*: the delays shown in the (sub)plot *deltaA/lambda*

- *specific wavelengths*: the wavelengths shown in the (sub)plot *delay/deltaA*

- *lower delay bound*: the chosen data of the `delays` will be cut off at the lower bound

- *upper delay bound*: the chosen data of the `delays` will be cut off at the upper bound

- *lower lambda bound*: the chosen data of the `lambda` will be cut off at the lower bound

- *upper lambda bound*: the chosen data of the `lambda` will be cut off at the upper bound

- *Contour lines*: a value characterizing the number of lines shown in the heatmap (sub)plot, higher values show more lines

### Settings for the Decay Associated Spectra

On the right side of the window, you can decide between the SAS and the DAS.

If you choose DAS, you will be asked to set `0`-`a` fixed and `0`-`b` variable values for the decay constants `tau` separated by commatas. The fixed values won't be optimized, whereas the variable ones will be incuded in the fit. The total number of tau values `a`+`b` has to be at least `1`.

<img src="/pictures/gui_DAS.png" width="30%"/>

### Settings for the Species Associated Spectra

If you choose SAS, you can decide between the models `1`-`9`, explained below, or a custom matrix. The preset models will generate a matrix K corresponding to the kinetics of the reaction. The custom matrix corresponds to the matrix K in the equation dC/dt = K * C.

<img src="/pictures/models.png" width="50%"/>

Also you will be asked to set `0` or `n` initial concentrations with `n` corresponding to the number of species separated by commatas. If you leave the panel empty, the concentration of specie `1` will be set to `1` and the concentration of the other species to `0`.

<img src="/pictures/gui_SAS_C.png" width="30%"/>

By clicking on *Next*, the next page will be opened, where you can specify the starting values for the lifetimes separated by commatas. If you choose a equilibrium model you have to fill in the forward and backward reaction lifetimes. For each lifetime you can define an upper and lower limit. They define the regions where the optimized lifetimes should be found. Should you not want to set a lower and/or upper limit for a certain lifetime, you can simply take `None` as an element of the list. 

<img src="/pictures/gui_SAS_k.png" width="30%"/>

### Start the calculation

Once you pushed the button *Ok* the calculation will start. Please be patient as the SAS can take longer than the DAS. When it's finished, the selected images as well as the results will pop up.

## Script

The general features of the GUI are also included in the script, although there are less settings regarding the plotting of single plots. However, this can be easily customized and will be explained at the end of this chapter.

### General settings

<img src="/pictures/skript_gen.png" width="50%"/>

First, you have to specify the `path` to the folder with your files. Files with the following names will be recognized:
> `folder/...lambda.txt` contains the wavelengths/nm,  
> `folder/...delays.txt` contains the delays/ps,  
> `folder/...spectra.txt` contains the absorption change.

On the top of the script, the general settings will be found.

There you can choose the `model`. The DAS will be calculated with a `0`, for the SAS you can set the models `1`-`9` (explained below) or `"custom"` for a custom matrix.

<img src="/pictures/models.png" width="50%"/>

The next settings are `l_limits` and `d_limits` which are the `[lower, upper]` bound for the `lambda` and `delays` where the original data will be cut off. Should you not want to set a lower and/or upper bound, you can simply take `None` as an element of the list. 

The variables `orig`, `fit` and `resi` affect which plots of the original and fitted data will be plotted.

For `orig` you can choose:

- `0`: no plot will be generated

- `3`: this will show the *all-in-one* plot of the original data

For `fit` you can choose:

- `0`: no plot will be generated

- `1`: the fitted values will be printed in the console and the results will be saved

<img src="/pictures/skript_fit1.png" width="50%"/>

- `2`: this will show the *all-in-one* plot of the fitted data and the results will be saved

<img src="/pictures/3-in-1-SAS.png" width="70%"/>

- `3`: with this option the values will be printed, the plot will be generated and the results will be saved

For `resi` you can choose:

- `0`: no plot will be generated

- `1`: the residuals will be plotted in a 1D plot of the residuals against the delays

<img src="/pictures/res_1D.png" width="30%"/>

- `2`: this will generate a 2D heatmap of the residuals

<img src="/pictures/res_2D.png" width="50%"/>

- `3`: with this option both images will be shown

This option only works, if fit is not 0.

### Settings for the Decay Associated Spectra

In the next section if you choose DAS, you have to set `0`-`a` fixed and `0`-`b` variable values for the decay constants `tau`. The fixed values won't be optimized, whereas the variable ones will be incuded in the fit. The total number of tau values `a`+`b` has to be at least `1`.

<img src="/pictures/skript_DAS.png" width="50%"/>

### Settings for the Species Associated Spectra

The settings for the SAS contain the lifetimes `tau_forwards` for the forward reactions and `tau_backwards`for the backward reactions in models `3` and `4`. The have to be entered in a list of lifetimes separated by commatas.

For each lifetime you can define an upper and lower limits for the forward (`tau_low_f`, `tau_high_f`) and backward reactions (`tau_low_b`, `tau_high_b`). They define the regions where the optimized lifetimes should be found. Should you not want to set a lower and/or upper limit for a certain lifetime, you can simply take `None` as an element of the list. If you wish not to set any bounds, write None instead of the list.

For the initial concentrations `C_0`, you will be asked to set `0` or `n` values with *n* corresponding to the number of species separated by commatas. If you leave the list empty, the concentration of species `1` will be set to `1` and the concentration of the other species to `0`.

Should you choose the model `"custom"` you can specify the matrix `M` at the end. It can be a list or an array either handwritten or imported from a file.

<img src="/pictures/skript_SAS.png" width="50%"/>

### Settings for the *all-in-one* plots

In the next section you can configure the settings for the *all-in-one* plots.

<img src="/pictures/skript_plot.png" width="50%"/>

You are offered the following possibilities:

- `wave`: the wavelengths shown in the (sub)plot *t/ΔA*

- `time`: the delays shown in the (sub)plot *ΔA/λ*

- `v_min` and `v_max`: the lower and upper boundaries for the colorbar in the heatmap, `None` for automatic determination.

- `cont`: a value characterizing the number of contour lines shown in the heatmap (sub)plot, higher values show more lines

- `mul`: the value by which the absorption data must be multiplied to get ΔA·10³

### Further customizing

The script can be used to better customize the images that will be generated.

If you want to create custom plots you can write the code below the calculation. Keep in mind that you still have to choose the right values for `model`, `d_limits`, `l_limits` and `C_0` in the settings at the beginning.

The methdod you will want to use to generate custom images is `Controller.plotCustom(wave, time, v_min, v_max, model, cont, custom, add, mul)`. Most of the variables have already been explained above.

*custom*: custom describes which subplots will be plotted

- `"1"`: chosen wavelength values will be plotted in a plot of the delays against the absorption change

<img src="/pictures/plot1.png" width="30%"/>

- `"2"`: the absorption change will be plotted as a heatmap of the delays against the wavelenghts

<img src="/pictures/plot2.png" width="50%"/>

- `"3"`: chosen delay values will be plotted in a plot of the absorption change against the wavelenghts

<img src="/pictures/plot3.png" width="30%"/>

- `"1+2"`, `"1+3"`, `"2+3"`, `"1+2+3"`: this is an image of the two or three plots mentioned above combined

The title of the plot corresponds to the name of the image. Be careful not to overwrite images and instead use `add` to give your plots different titles.

Another plot can be plotted with `Controller.plotKinetics(model)`. It shows the concentration of each species against the delays.

Furthermore the DAS or SAS can be plotted with `Controller.plotDAS(model, tau_fit)`. It is a plot of the absorption change against the wavelengths.

The images for both of the plots are presented in the section of the GUI.
