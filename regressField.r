#import data
setwd("C:/Users/liaos/OneDrive/Documents/Brown/Senior Year/GISPMidterm")
runStats <- read.csv("run_stats_fixed.csv")

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

# Merge with the RunStats Dataset
teamsNonYPC <- teams[, c(1:5)]
colnames(teamsNonYPC) <- c('homeId', 'homeOCarries', 'homeACarries', 'homeOYards', 'homeAYards') 
runStats <- merge(runStats, teamsNonYPC, by= "homeId")

colnames(teamsNonYPC) <- c('awayId', 'awayOCarries', 'awayACarries', 'awayOYards', 'awayAYards') 
runStats <- merge(runStats, teamsNonYPC, by= "awayId")

# Now adjust to remove current game:
runStats$homeOCarriesAdj <- runStats$homeOCarries - runStats$home.carries
runStats$awayACarriesAdj <- runStats$awayACarries - runStats$home.carries

runStats$homeOYardsAdj <- runStats$homeOYards - runStats$home.yards
runStats$awayAYardsAdj <- runStats$awayAYards - runStats$home.yards

runStats$awayOCarriesAdj <- runStats$awayOCarries - runStats$away.carries
runStats$homeACarriesAdj <- runStats$homeACarries - runStats$away.carries

runStats$awayOYardsAdj <- runStats$awayOYards - runStats$away.yards
runStats$homeAYardsAdj <- runStats$homeAYards - runStats$away.yards

# Finally get Adjusted Offense and Defense
runStats$homeOffenseYPC <- runStats$homeOYardsAdj / runStats$homeOCarriesAdj
runStats$homeDefenseYPC <- runStats$homeAYardsAdj/ runStats$homeACarriesAdj
runStats$awayOffenseYPC <- runStats$awayOYardsAdj / runStats$awayOCarriesAdj
runStats$awayDefenseYPC <- runStats$awayAYardsAdj / runStats$awayACarriesAdj

# Now filter for only the fields we need

runStats_filter <- runStats[, c(3, 8, 4, 13, 15, 14, 33:36)]

# We want a dataset with columns:
# year, home or away, team, ypc, how good this team is at rushing, how good the defense is against rushing attacks

# So we split up our current dataset to have the entries we want
homeTeams <- runStats_filter[, c(1,2,4,5,7,10)]
awayTeams <- runStats_filter[, c(1,3,4,6,8,9)]

# Add homeOrAway column
homeTeams$homeOrAway <- "Home"
awayTeams$homeOrAway <- "Away"

# Set it so all column names are the same 
colnames(homeTeams)[c(2, 4:6)] <- c("team", "gameYPC", 'offenseYPC', 'defenseYPCAllowed')
colnames(awayTeams)[c(2, 4:6)] <- c("team", "gameYPC", 'offenseYPC', 'defenseYPCAllowed')

# Bind em together
final_data_regression <- rbind(homeTeams, awayTeams)

# Run regression

mod <- lm(gameYPC ~ homeOrAway, data = final_data_regression)