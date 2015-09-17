import matplotlib.pyplot as plt
from skimage import exposure

def show_comparison(im1, im2, title1, title2, xmin, xmax, ymin, ymax, hist1=False, hist2=False, cmap1=plt.cm.gray, cmap2=plt.cm.gray):
    bins=100

    if hist1 or hist2:
        fig, ax = plt.subplots(3, 2, figsize=(20, 15))
        ax1, ax2, ax3, ax4, ax5, ax6 = ax.ravel()
    else:
        fig, ax = plt.subplots(2, 2, figsize=(20, 10))
        ax1, ax2, ax3, ax4 = ax.ravel()

    ax1.imshow(im1, cmap=cmap1,interpolation='nearest')
    ax1.set_title(title1)
    ax1.axis('off')

    ax2.imshow(im2, cmap=cmap2,interpolation='nearest')
    ax2.set_title(title2)
    ax2.axis('off')

    ax3.imshow(im1[xmin:xmax, ymin:ymax], cmap1,interpolation='nearest')
    ax3.axis('off')

    ax4.imshow(im2[xmin:xmax, ymin:ymax], cmap2,interpolation='nearest')
    ax4.axis('off')

    if hist1:
        # Display histogram
        ax5.hist(im1.ravel(), bins=bins, histtype='step', color='black')
        ax5.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        ax5.set_xlabel('Pixel intensity')
        ax5.set_xlim(0, 1)
        ax5.set_yticks([])

        # Display cumulative distribution
        ax5_cdf = ax5.twinx()
        img_cdf, bins = exposure.cumulative_distribution(im1, bins)
        ax5_cdf.plot(bins, img_cdf, 'r')
        ax5_cdf.set_yticks([])

    if hist2:
        # Display histogram
        ax6.hist(im2.ravel(), bins=bins, histtype='step', color='black')
        ax6.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        ax6.set_xlabel('Pixel intensity')
        ax6.set_xlim(0, 1)
        ax6.set_yticks([])
        
        # Display cumulative distribution
        ax6_cdf = ax6.twinx()
        img_cdf, bins = exposure.cumulative_distribution(im2, bins)
        ax6_cdf.plot(bins, img_cdf, 'r')
        ax6_cdf.set_yticks([])
        
    fig.subplots_adjust(hspace=0.02, wspace=0.02, top=1, bottom=0, left=0, right=1)

def show_im(im, title, xmin, xmax, ymin, ymax, cmap=plt.cm.gray, histogram=True):
    bins=600
    
    if histogram:
        fig, ax = plt.subplots(1, 3, figsize=(20, 5))
        ax1, ax2, ax3 = ax.ravel()
    else:
        fig, ax = plt.subplots(1, 2, figsize=(20, 5))
        ax1, ax2 = ax.ravel()

    ax1.imshow(im, cmap=cmap,interpolation='nearest')
    ax1.set_title(title)
    ax1.axis('off')

    ax2.imshow(im[ymin:ymax, xmin:xmax], cmap,interpolation='nearest')
    ax2.axis('off')

    if histogram:
        # Display histogram
        ax3.hist(im.ravel(), bins=bins, histtype='step', color='black')
        ax3.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        ax3.set_xlabel('Pixel intensity')
        ax3.set_xlim(0, 1)
        ax3.set_yticks([])

        # Display cumulative distribution
        ax3_cdf = ax3.twinx()
        img_cdf, bins = exposure.cumulative_distribution(im, bins)
        ax3_cdf.plot(bins, img_cdf, 'r')
        ax3_cdf.set_yticks([])
