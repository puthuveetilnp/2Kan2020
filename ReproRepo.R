library(shinydashboard)
library(tidyverse)
library(shinydashboardPlus)
library(readxl)
library(spData)
library(DT)
library(shinyWidgets)
library(reticulate)
library(sf)
library(tmap)
library(shinycustomloader)
source_python("TF_IDF.py")
  

highlight <- function(text, search) {
  x <- unlist(strsplit(text, split = " ", fixed = T))
  x[tolower(x) %in% tolower(c(search))] <- paste0("<mark>", x[tolower(x) %in% tolower(c(search))], "</mark>")
  paste(x, collapse = " ")

}

extracted_highlighted_text <- function(text, search) {
  x <- unlist(strsplit(text, split = " ", fixed = T))
  found_words <- x[tolower(x) %in% tolower(c(search))]
  
  return(found_words)
}

# Retrieve fake_phrases.xlsx
fake_phrases = read_excel("fakephrases.xlsx")


# Extract states
df <- read_excel("cpc-list_uncleaned.xlsx")
total_fake_clinics <- df %>% select("State") %>% group_by(State) %>% tally() %>% 
  rename("Total Number of Fake Clinics" = "n") 

# Get population and state geometry data
states <- data.frame(state.name, state.abb)
names(states) <- c("State Name", "State")
state_geometry <- us_states
names(state_geometry)[names(state_geometry) == "NAME"] <- "State Name"

# Merge with cpc list
total_fake_clinics <- merge(total_fake_clinics, states, by="State")
final <- merge(total_fake_clinics, state_geometry, by="State Name")

# Normalize data
final$normalized <- final$`Total Number of Fake Clinics`/final$total_pop_15 * 1e6
final <- final %>% rename("Number of Fake Clinics Per Million" = "normalized")
fake_clinic_density <- st_sf(final)

ui <- dashboardPage(skin = "purple",
  dashboardHeader(title = "2KAN"),
  dashboardSidebar(
    sidebarMenu(
            menuItem("About Us", tabName = "about", icon = icon("dashboard")), 
            menuItem("URL Checker", tabName = "widget", icon = icon("search"),
                     badgeLabel = "new", badgeColor = "green"), 
            menuItem("Reliable sources", tabName = "sources"))),
  dashboardBody(
    tabItems(
      tabItem(tabName = "about", 
              fluidRow(
                widgetUserBox(
                  title = "ReproRepo",
                  subtitle = "Nonprofit",
                  type = NULL,
                  width = 12,
                  src = "https://www.freeiconspng.com/thumbs/flowers-icon-png/flower-lotus-nature-plant-water-plant-icon-28.png",
                  background = TRUE,
                  backgroundUrl = "https://images.pexels.com/photos/531880/pexels-photo-531880.jpeg?auto=compress&cs=tinysrgb&h=350",
                  closable = FALSE,
                  "About us:",
                  footer = "ReproRepo is a tool devoted to dispelling misinformation on reproductive health. No matter what your opinions may be, we believe all people deserve to
                have access to reputable, honest information. No lies and no deception."
                )
              ),
              box(
                title = "Number of Fake Clinics Nationwide",
                status = "warning",
                width = NULL,
                radioGroupButtons(
                  inputId = "graphChoices",
                  label = "Graph View", 
                  choices = c("By Number of Fake Clinics Per Million", "By Total Number of Fake Clinics"),
                  status = "primary"
                ),
                fluidRow(
                  column(
                    width = 6,
                    boxPad(
                      dataTableOutput("clinicNums")
                    )
                  ),
                  column(
                    width = 6,
                    tmapOutput("fakeclinics")
                    )
                  )
                )
              ),
      tabItem(tabName = "widget",
              widgetUserBox(
                title = "ReproRepo URL Checker",
                subtitle = "How honest are these clinics in what they offer?",
                type = NULL,
                width = 12,
                src = "https://www.freeiconspng.com/thumbs/flowers-icon-png/flower-lotus-nature-plant-water-plant-icon-28.png",
                background = TRUE,
                backgroundUrl = "https://images.pexels.com/photos/531880/pexels-photo-531880.jpeg?auto=compress&cs=tinysrgb&h=350",
                closable = FALSE,
                "About us:",
                footer = "At 2Kan2020, we believe that all individuals should get the care they believe they are receiving and be well informed in the choices they make. The Internet is a great place to learn more, but
                reader beware, the world wide web has a lot of deceptive and outdated information. We strive to dispel false and deceptive information one website at a time, starting with pregnancy misinformation.
                We've devised a ReproRepo URL Checker Tool that, with the input of a URL of a pregnancy resource, we'll let you know how accurate the information is."
              ),
              box(title = "URL Checker",
                  width = 9,
                  status = "warning",
                  textInput("user_url", "Enter a url:", value=""),
                  actionButton("url_entered", "Submit!"),
                  withLoader(textOutput("results"), type="html", loader='pacman')
                  #withLoader(verbatimTextOutput("scraped_data", placeholder=TRUE), type="html", loader="pacman")
                  )
              )
    )
  )
)


server <- function(input, output) {
  
  get_results = reactive({
    result <- unlist(get_user_sim_score(input$user_url))
    if(length(result) > 0){
      text = paste("Our analysis shows that the information on this website is mostly likely", result[3], 
                   ". This website matched to",  result[2], "fake clinic websites and matched to",  result[1], "credible websites")
    }
      
    else{
      text = "Oops! Seems like the website might be down or doesn't exist anymore."
    }
    return(text)})
  
  observeEvent({input$graphChoices},
               if(input$graphChoices == "By Number of Fake Clinics Per Million"){
                 output$fakeclinics <- renderTmap({tm_shape(fake_clinic_density) + tm_polygons("Number of Fake Clinics Per Million", title="Number of Fake Clinics Per Million People")}
                 )
               }
               else{
                 output$fakeclinics <- renderTmap({tm_shape(fake_clinic_density) + tm_polygons("Total Number of Fake Clinics", title="Total Number of Fake Clinics")}
                 )
               })
  
  observeEvent({input$url_entered},
               output$results <- renderText({get_results()}),
               #output$scraped_data <- renderText({get_text(input$user_url)})
               )
  
  
  output$clinicNums <- renderDataTable(final %>% select("State Name", "Number of Fake Clinics Per Million", "Total Number of Fake Clinics"))

}

shinyApp(ui, server)
