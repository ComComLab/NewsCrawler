
rm(list=ls())
library(rvest)
library(RSelenium)
library(tidyverse)
library(stringr)
remDr <- remoteDriver()
remDr$open()
Month <- c(rep(9,7),rep(10,31),rep(11,24))
Month <- ifelse(Month<10,paste0(0,Month),Month)
Day <- c(24:30,1:31,1:24)
Day <- ifelse(Day<10,paste0(0,Day),Day)
Links <- c()
for(i in 1:length(Month)){
  remDr$setTimeout(type = "page load", milliseconds = 10000)
  print(paste0("Month: ",Month[i]," Days:",Day[i]))
  url <- paste0("https://www.chinatimes.com/history-by-date/2018-",Month[i],"-",Day[i],"-260407")
  remDr$navigate(url)
  span <- remDr$findElement(using="xpath",
                            "/html/body/div[1]/div[3]/article/section[1]/div[2]/div[1]/ul/li[5]/a/span[2]")
  
  page <- read_html(span$getElementAttribute("outerHTML")[[1]]) %>% html_text()
  page <- ceiling(as.numeric(str_extract(page,"\\d+"))/11)
  
  for(p in 1:page){
    print(paste0("page: ",p))
    urls <- paste0(url,"?page=",p)
    remDr$navigate(urls)
    links <- read_html(listright$getElementAttribute("outerHTML")[[1]]) %>%
      html_nodes('h2 a') %>% html_attrs()
    for(a in links){
      link <- paste0("https://www.chinatimes.com",a[1])
      Links <- c(Links,link)
    }
  }
}

Links <- Links[!duplicated(Links)]
result <- NULL
for(i in 1:length(Links)){
  print(i)
  a <- Links[i]
  a
  html <- read_html(a)
  title <- html %>% 
    html_node("h1") %>% 
    html_text()
  title <- gsub("\r\n                ","",title)
  title <- gsub("\r\n","",title)
  
  datetime <- html %>% 
    html_node("div time") %>%
    html_text()
  date_time <- gsub("\r\n                    ","",datetime)
  
  content <- html %>% 
    html_nodes("article") %>%
    html_nodes("p") %>%
    html_text()
  content <- paste(content,collapse =" ")
  re <- data.frame(date_time,title,content)
  result <- rbind(result,re)
  #Sys.sleep(2)
}
#save(result,file='result.RData')
write.table(result,"result.csv",row.names = F,sep=',')
