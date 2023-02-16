# **EfsTA**

## **About the program**

*EfsTA* stands for **E**valuation of **f**emto**s**econd **t**ransient **A**bsorption spectroscopy data and, like the name suggest, is a program for the evaluation of transient absorption spectroscopy data. It is entirely written in Python and makes use of the many useful libraries for scientific calculations like numpy and scipy. In contrast to many other programs which use Single Value Decomposition (SVD), *EfsTA* uses a matrix reconstruction algorithm. It was created by *Natalia Schmidbauer* and *Lucas Tränkle (4-DMAPandSadness)* for their bachelors thesis and is maintained by *Lucas Tränkle*. The goal was to create a free to use program for the analysis of fsTA data in a userfriendly way by providing a fully fleshed out GUI, so that the evaluation can be done even by people without any programming experience whatsoever.

## **Key Features**

+ Easy to use GUI and script form

+ Darkmode

+ Both GLA and GTA in one program

+ Fast fitting and error calculations via lmfit

+ Eight preimplemented kinetic models

+ Easy implementation of custom kinetic models by providing only a "reaction equation" for the transitions

+ Possibility to directly input the "reaction matrix"

+ Many different plots

## **Dependencies**

NumPy, SciPy, asteval, uncertainties, lmfit, PyQt, matplotlib




