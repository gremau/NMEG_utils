printfigs <- function(fig, filename, w, h, multi=0) {
  # pass a figure or list of figures
  # if multi is greater than 0, it will treat a list of figures as a multiplot
  # Prints to two locations.
  
  source('~/data/code_resources/r_common/multiplot.r')
  
  # Choose printing device
  if (grepl('.svg', filename)) {device <- svg}
  else if (grepl('.eps', filename)) {device <- cairo_ps}
  else if (grepl('.pdf', filename)) {device <- cairo_pdf}
  
  # If fig is a list, but multiplot is not requested, print 1 at a time
  if (class(fig)[[1]]=="list") {
    if (multi==0) {
      for (i in figlist) {
        device(paste("../figures/", filename[[i]], sep=""),
                   onefile=FALSE,
                   width=w, height=h, bg='white', pointsize=14)
        print(fig[[i]])
        dev.off()
        
#         device(paste("../../manuscript_1/figs/", filename[[i]], sep=""),
#                    onefile=FALSE,
#                    width=w, height=h, bg='white', pointsize=14)
#         print(fig[[i]])
#         dev.off()
      }
    }
    # If fig is a list, multiplot IS requested, make it and print it
    else if (multi>0){
      device(paste("../figures/", filename, sep=""),
                 onefile=FALSE,
                 width=w, height=h, bg='white', pointsize=14)
      multiplot(plotlist=fig, cols=multi)
      dev.off()
      
#       device(paste("../../manuscript_1/figs/", filename, sep=""),
#                  onefile=FALSE,
#                  width=w, height=h, bg='white', pointsize=14)
#       multiplot(plotlist=fig, cols=multi)
#       dev.off()
    }
  }

  # Otherwise just print it
  else {
    device(paste("../figures/", filename, sep=""),
               onefile=FALSE,
               width=w, height=h, bg='white')
    print(fig)
    dev.off()
    
#     device(paste("../../manuscript_1/figs/", filename, sep=""),
#                onefile=FALSE,
#                width=w, height=h, bg='white')
#     print(fig)
#     dev.off()
  }
}
