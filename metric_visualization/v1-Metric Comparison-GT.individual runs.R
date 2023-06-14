####
# Generates visualizations of the NLP metrics
# Run this file each time filtering out different levels of the Ground Truth variable.
# each run, set 'property' and 'folder' variables as appropriate.
# Should be outputting the visualizations in figs/v1
####


# Load required packages
library(ggplot2)
library(dplyr)

# Read the CSV file
data <- read.csv("data/randomValues.csv")

#data Filtering by Ground Truth
# property <- "manual"; folder <-"manual"
# property <- "baseline"; folder <- "baseline"
property <- "additional"; folder <- "additional"
data <- data %>% filter(gt != property)

# Set Data columns as factors
data$Audience <- factor(data$Audience)
data$Example.Type <- factor(data$Example.Type)
data$User.Number <- factor(data$User.Number)

levels(data$Audience) <- c("None", "Self", "Peer", "Manager")
levels(data$Example.Type) <- c("None", "Manual", "Manual Masked", "Template Masked")

# Define the factor levels for color and assign them to the first two columns
# colors <- c("red", "blue", "green", "yellow") # too gaudy
# colors <- c("#570047", "#82036A", "#A70F88", "#C621A3", "#CF3FCA", "#C45DD7", "#BD7BDF", "#BF9AE7") #Too many steps.
colors <- c("#570047", "#a8194b", "#e55838", "#ffa600")
shapes <- c(15,16,17,18) #solid Square, Circle, Triangle, Diamond
factors <- c("Audience", "Example", "User")

# Generate scatterplots for each pair of columns
for (i in 5:(length(data)-1)) {
  for (j in (i + 1):length(data)) {
    # Create a new plot for each pair of columns
    plot_title <- paste(colnames(data)[i], "vs.", colnames(data)[j])
    p <- ggplot(data, aes_string(x = colnames(data)[i], y = colnames(data)[j])) +
      # geom_point(aes(color = factor(.data[[factors[1]]]), shape = factor(.data[[factors[2]]])),
      geom_point( aes(color = Audience, shape = Example.Type),
                  size = 3) +
      scale_color_manual(values = colors) +
      # scale_shape(solid=TRUE, name = "Example Type")+
      scale_shape_manual(values = shapes, name = "Example Type")
    labs(title = plot_title, x = colnames(data)[i], y = colnames(data)[j])
    
    # Save the plot as an image
    ggsave(filename = paste0("figs/v1/",folder,"/scatterplot_", colnames(data)[i], "_", colnames(data)[j], ".png"), plot = p)
    
    # Print the plot
    print(p)
  }
}


get_min_max <- function(column_name) {
  # Find the column index with the same name
  col_index <- match(column_name, names(data))
  
  # Check if the column exists
  if (is.na(col_index)) {
    stop("Column '", column_name, "' does not exist in the data.")
  }
  
  # Calculate the minimum and maximum values of the column
  min_value <- min(data[, col_index], na.rm = TRUE)
  max_value <- max(data[, col_index], na.rm = TRUE)
  
  # print(paste(min_value,"< x < ",max_value))
  
  # Return the results as a list
  result <- c(min_value, max_value)
  return(result)
}


#make a list of the column names
cont.vars <- colnames(data)[5:length(data)]

#generate faceted scatterplots for each column
for(k in cont.vars){
  p <- ggplot(data=data, 
              aes_string(x="Audience", y=k, 
                         group="User.Number",
                         shape="User.Number",
                         color="User.Number")) + 
    geom_point(size = 3) +
    scale_color_manual(values = colors) + #, name = "User ID") +
    # scale_shape_manual(values = shapes, name = "User ID") + 
    # geom_boxplot()+
    labs(title =
           paste0(k," by Audience, Example Type, and User Number")) +
    scale_x_discrete("Audience") +
    # scale_y_continuous(limits = c(0,1)) + 
    scale_y_continuous(limits = get_min_max(k)) +
    facet_grid(.~Example.Type )
  print(p)
  ggsave(filename = paste0("figs/v1/",folder,"/faceted-",k,".png"), plot = p)
}


