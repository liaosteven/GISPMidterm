#import data
setwd("C:/Users/liaos/OneDrive/Documents/Brown/Senior Year/GISPMidterm")
runStats <- read.csv("run_stats_data.csv")

# Create YPC variables
runStats$awayYPC <- runStats$away.yards / runStats$away.carries
runStats$homeYPC <- runStats$home.yards / runStats$home.carries
runStats$YPC <- (runStats$away.yards + runStats$home.yards)/(runStats$away.carries + runStats$home.carries)

# Convert variables from factors to characters
i <- sapply(runStats, is.factor)
runStats[i] <- lapply(runStats[i], as.character)

# Create home and away ID's
runStats$homeId <- paste(runStats$hometeam, runStats$year)
runStats$awayId <- paste(runStats$awayteam, runStats$year)

# Now we create a new Data Frame for the teams. 
# This will be for calculating team defense + rushing strength later on
# - which we will adjust for in our model
teams <- as.data.frame(unique(runStats$homeId))
names(teams) <- c("team_id")

# Aggregate by ID function
aggById <- function(values, group, id) {
  finalSum <- sum(values[group == id])
  return(finalSum)
}

teamCarries <- function(id, own) {
  
  if (own) {
    homeCarries <- aggById(runStats$home.carries, runStats$homeId, id)
    awayCarries <- aggById(runStats$away.carries, runStats$awayId, id)
  }else {
    homeCarries <- aggById(runStats$away.carries, runStats$homeId, id)
    awayCarries <- aggById(runStats$home.carries, runStats$awayId, id)
  }
  return (homeCarries + awayCarries)
}

teamYards <- function(id, own) {
  
  if (own) {
    homeYards <- aggById(runStats$home.yards, runStats$homeId, id)
    awayYards <- aggById(runStats$away.yards, runStats$awayId, id)
  } else {
    homeYards <- aggById(runStats$away.yards, runStats$homeId, id)
    awayYards <- aggById(runStats$home.yards, runStats$awayId, id)
  }
  return (homeYards + awayYards)
}

teams$ownCarries <- sapply(teams$team_id,teamCarries, 1)
teams$againstCarries <- sapply(teams$team_id, teamCarries, 0)
teams$ownYards <- sapply(teams$team_id, teamYards, 1)
teams$againstYards <- sapply(teams$team_id, teamYards, 0)

teams$ownYPC <- teams$ownYards / teams$ownCarries
teams$againstYPC <- teams$againstYards / teams$againstCarries
