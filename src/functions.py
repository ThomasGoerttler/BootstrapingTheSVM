import os
import sys

from multiprocessing import Process, Pool
from numpy import *
from sklearn import svm
from models import *

import matplotlib.pyplot as plt
import math
import statistics
import random
import datetime


def do_Bootstrap(trainings_data, prediction_data, kernel, C, gamma = "auto", degree = 3, processes = 1, replications = 10):

    
    input_parameters = SVM_Input(trainings_data, prediction_data, kernel, C, gamma, degree)

    data = input_parameters
    real_svm = do_svm(data)
    
    ### Do bootstrapping
    PROCESSES = processes
    REPLICATIONS = replications
    pool = Pool(processes = PROCESSES)
    results = pool.map(single_sample_and_svm, [data] * REPLICATIONS)
        
    ### Calculate the Variance of the Support Vector Machine
    
    points_information = Points_Information(results)
    
    variance_of_svm_probabilites = calculate_variance_of_svm(points_information.probabilites)
    variance_of_svm_distance_to_hyperplane = calculate_variance_of_svm(points_information.distances)
        
    return([real_svm[0], real_svm[1], variance_of_svm_probabilites, variance_of_svm_distance_to_hyperplane])
    
    
def random_sample_with_replacement(population, sample_size):
    "Chooses k random elements (with replacement) from a population"
    n = len(population)
    _random, _int = random.random, int  # speed hack
    return [_int(_random() * n) for i in range(sample_size)]

def random_sample_with_replacement_of_dataset(data, sample_size):
    y, x = data
    sorted_list = sorted(random_sample_with_replacement(range(len(y)), sample_size))
    y = [y[i] for i in sorted_list]
    x = [x[i] for i in sorted_list]
    return(y, x)
        

def single_sample_and_svm(input_parameters):
    "New version of using skilearn"
    
    #training_data, prediction_data = input_parameters
    
    training_data = input_parameters.training_data
    prediction_data = input_parameters.prediction_data
    kernel = input_parameters.kernel
    
    # Set seed for each Thread new as otherwise each process starts with same Seed -> ugly
    SEED = datetime.datetime.now().time().microsecond
    random.seed(SEED)
    
    y, X = random_sample_with_replacement_of_dataset(training_data, len(training_data[0]))
    
    clf = svm.SVC(probability = True, kernel = kernel, C = input_parameters.C, gamma = input_parameters.gamma, degree = input_parameters.degree )
    fit = clf.fit(X, y)  
    
    yy = 0
    
    distance_to_hyperplane = clf.decision_function(prediction_data[1])
    probabilities = clf.predict_proba(prediction_data[1])
    probabilities = list(zip(*probabilities))
    probabilities = probabilities[1]
    
    
    result = SVM_Result(probabilities, distance_to_hyperplane, yy, clf.n_support_, 0)
    
    return(result)
    
    
def do_svm(input_parameters):
    
    training_data = input_parameters.training_data
    prediction_data = input_parameters.prediction_data
    kernel = input_parameters.kernel
    
    y, X = training_data
    
    clf = svm.SVC(probability = True, kernel = kernel, C = input_parameters.C, gamma = input_parameters.gamma, degree = input_parameters.degree )
    fit = clf.fit(X, y)  
    
    
    score = clf.score(prediction_data[1],prediction_data[0])
    
    
    return(clf, score)
    

def calculate_variance_of_svm(results):
    
    # Creating an empty array with size of points
    standard_deviations = [None] * len(results)
    
    # For each point the standard deviation of the different predicted values will be calculated
    for index in range(len(results)):
        std = statistics.stdev(results[index])
        standard_deviations[index] = std
        
    return(statistics.mean(standard_deviations))
    
    
def invert(matrix):
    return(list(zip(*matrix)))