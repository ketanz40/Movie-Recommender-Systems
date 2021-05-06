import csv
import json

def readMovies(write):
    movies = {}
    
    with open("movies.csv", encoding="UTF-8") as csvFile:
        if write: knowledgeBase = open("knowledge_base.pl", "w", encoding = "UTF-8")
        reader = csv.reader(csvFile)
        lines = 0
        for row in reader:
            if lines == 0:
                lines += 1
            else:
                genre = row[1].split("|")
                genre = [genre[i].strip() for i in range(len(genre))]    
                actors = row[2].split("|")
                size = len(actors) if len(actors) < 5 else 5
                actors = [actors[i].strip() for i in range(size)]
                companies = row[5].split("|")
                size = 2 if len(companies) > 1 else 1
                companies = [companies[i].strip() for i in range(size)]

                movies[row[0]] = [genre, actors, row[3], float(row[4]), companies]
                fact = "film({}, [{}], [{}], {}, {}, [{}]).\n".format(f'"{row[0]}"', ",".join(f'"{w}"' for w in genre), ",".join(f'"{w}"' for w in actors), f'"{row[3]}"', row[4], ",".join(f'"{w}"' for w in companies))
                if write: knowledgeBase.write(fact)
    
    return movies

def watchedMovies(watched, movies):
    features = [set(), set(), set(), [], set()]
    
    for movie in watched:
        mFeatures = movies[movie]
        for i in range(len(mFeatures)):
            if isinstance(mFeatures[i], list):
                for feature in mFeatures[i]:
                    features[i].add(feature)
            else:
                if i == 3: features[i].append(mFeatures[i])
                else: features[i].add(mFeatures[i])

    numRatings = len(features[3])
    from functools import reduce
    import operator
    mean = reduce(operator.add, features[3]) / numRatings
    features[3] = mean
    
    return features



movies = readMovies(False)

watchedMoviesList = ["Mission: Impossible - Fallout", "Mission: Impossible - Ghost Protocol", "Spectre",  "Batman Begins"]
features = watchedMovies(watchedMoviesList, movies)

from pyswip import Prolog

prolog = Prolog()
prolog.consult("knowledge_base.pl")

query = "recommendActors(["

query += ",".join(f'"{w}"' for w in features[1])
query += "], {}, Movie)".format(1 / len(features[1]))

print("Watched movies: ", watchedMoviesList)
print()
print(query)
print("\nRecommended Movies: ")
i = 0
for soln in prolog.query(query):
    if i < 100: 
        movie = soln["Movie"].decode("UTF-8")
        if movie not in watchedMoviesList: 
            print(movie)
            i += 1
    else: break