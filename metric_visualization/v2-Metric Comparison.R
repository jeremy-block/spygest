####
# Generates visualizations of the NLP metrics
# Will generate pairwise comparisons for each metric, as well as faceted views by participant number and by ground truth type.
# Should be outputting the visualizations in figs/v2
####


# Load required packages
library(ggplot2)
library(dplyr)

# Read the CSV file
data <- read.csv("data/randomValues.csv")

# Set Data columns as factors
data$Audience <- factor(data$Audience)
data$Example.Type <- factor(data$Example.Type)
data$User.Number <- factor(data$User.Number)
data$Ground.Truth <- factor(data$Ground.Truth)

levels(data$Audience) <- c("None", "Self", "Peer", "Manager")
levels(data$Example.Type) <- c("None", "Manual", "Manual Masked", "Template Masked")
levels(data$Ground.Truth) <- c("manual", "baseline", "additional")

# Define the factor levels for color and assign them to the first two columns
# colors <- c("red", "blue", "green", "yellow") # too gaudy
# colors <- c("#570047", "#82036A", "#A70F88", "#C621A3", "#CF3FCA", "#C45DD7", "#BD7BDF", "#BF9AE7") #Too many steps.
colors <- c("#570047", "#a8194b", "#e55838", "#ffa600")
shapes <- c(15,16,17,18) #solid Square, Circle, Triangle, Diamond
factors <- c("Audience", "Example", "User")

folder <- "by_metric_pairs"

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
    ggsave(filename = paste0("figs/v2/",folder,"/scatterplot_", colnames(data)[i], "_", colnames(data)[j], ".png"), plot = p)
    
    # Print the plot
    print(p)
  }
}

####### New



library(lattice)

# Create a sample data frame
data <- data.frame(
  x = rep(1:10, 2),  # x values
  y = c(rnorm(10), rnorm(10, mean = 2)),  # y values
  group = rep(c("Group 1", "Group 2"), each = 10)  # group labels
)

# Create a scatter plot with small multiples
xyplot(y ~ x | group, data = data, type = "p", layout = c(1, 2))

# Create line plots with small multiples
xyplot(y ~ x | group, data = data, type = "l", layout = c(1, 2))

# xyplot(data = data, )




####### /new


folder <- "by_user"

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
  ggsave(filename = paste0("figs/v2/",folder,"/faceted-",k,".png"), plot = p)
}



folder <- "by_ground_truth"

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
                         group="Ground.Truth",
                         shape="Ground.Truth",
                         color="Ground.Truth")) + 
    geom_point(size = 3) +
    scale_color_manual(values = colors) + #, name = "User ID") +
    # scale_shape_manual(values = shapes, name = "User ID") + 
    # geom_boxplot()+
    labs(title =
           paste0(k," by Audience, Example Type, and Ground Truth")) +
    scale_x_discrete("Audience") +
    # scale_y_continuous(limits = c(0,1)) + 
    scale_y_continuous(limits = get_min_max(k)) +
    facet_grid(.~Example.Type )
  print(p)
  ggsave(filename = paste0("figs/v2/",folder,"/faceted-",k,".png"), plot = p)
}



