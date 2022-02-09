import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sb

def plot_mean(ds,var,ax=None,low_alt=0,high_alt=8000,dim='circle',c='k',label=''):
    
    ds.sel(alt=slice(low_alt,high_alt))[var].mean(dim=dim).plot(ax=ax,y='alt',c=c,label=label)

    return ax

def iqr(ds,var,low_alt=0,high_alt=8000,dim='circle'):
        
    lowq = ds.sel(alt=slice(low_alt,high_alt))[var].quantile(0.25,dim=dim)
    highq = ds.sel(alt=slice(low_alt,high_alt))[var].quantile(0.75,dim=dim)
    
    return lowq, highq

def plot_iqr(ds,var,ax=None,low_alt=0,high_alt=8000,dim='circle',c='grey',label=''):
    
    alt = ds.alt.sel(alt=slice(low_alt,high_alt))
    
    lowq, highq = iqr(ds,var,low_alt,high_alt,dim=dim)
    
    if ax is not None :
        ax.fill_betweenx(alt,lowq,highq,alpha=0.5,color=c,label=label)
    else :
        plt.gca().fill_betweenx(alt,lowq,highq,alpha=0.5,color=c,label=label)
        
    return ax

def plot_iqr_mean(ds,var,ax=None,low_alt=0,high_alt=8000,dim='circle',
                  mean_c='k',iqr_c='grey',
                  label=True,
                  mean_label='Mean',iqr_label='IQR'):
    
    plot_mean(ds,var,ax,low_alt,high_alt,dim=dim,c=mean_c,label=mean_label if label else '')
    plot_iqr(ds,var,ax,low_alt,high_alt,dim=dim,c=iqr_c,label=iqr_label if label else '')
    
    return ax