# General models for any amount of species

# Model 1: A -> B -> C ... -> Z -> 0
# Model 2: A -> B -> C ... -> Z
# Model 3: A <=> B <=> C ... <=> Z -> 0
# Model 4: A <=> B <=> C ... <=> Z

# Specific models for a certain amount of species

# Model 5: A -> B -> C -> D; B -> D
# Model 6: A -> B -> C -> D -> E; B -> E
# Model 7: A -> B -> C -> D -> E; C -> E
# Model 8: A -> B -> C -> D -> E -> F; C -> F
# Model 9: A -> B; A -> C
# Model 10: A -> B ; B -> C ; B -> D

import numpy as np


class Models:

    # Initiator

    def __init__(self, ks):
        '''

        The Initiator generates the objects with the necessary parameters and
        data.

        Parameters
        ----------
        k : np.array
            A onedimensional numpy array which containes the given reaction
            rate constants, with which the species 'decay'.

        Returns
        -------
        None.

        '''
        self.k = ks

    # General models

    def getK(self, model):
        if model == 1:
            K, n = self.model1()
        elif model == 2:
            K, n = self.model2()
        elif model == 3:
            K, n = self.model3()
        elif model == 4:
            K, n = self.model4()
        elif model == 5:
            K, n = self.model5()
        elif model == 6:
            K, n = self.model6()
        elif model == 7:
            K, n = self.model7()
        elif model == 8:
            K, n = self.model8()
        elif model == 9:
            K, n = self.model9()
        elif model == 10:
            K, n = self.model10()
        return K, n

    def model1(self):
        '''

        Model 1: A -> B -> C ... -> Z -> 0

        Creates two arrays from the given reaction rate constants. One for the
        main diagonal of the matrix K, which corresponds to the loss in
        concentration for each species. The other one for the diagonal under
        the main diagonal, which corresponds to the gain in concentration for
        each species. Then generates the matrix K.

        In this model the last species reacts into nothingness.

        Returns
        -------
        K_lin : np.array
            A 2D array which corresponds to the reaction rate constant matrix
            for a linear decay with n-species.

        '''
        k_hin = self.k
        k1 = np.array(k_hin) * (-1)
        k2 = k1.copy()*(-1)
        k2 = np.delete(k2, -1)
        K_lin = np.diag(k2, k=-1)
        np.fill_diagonal(K_lin, k1)
        n = len(k_hin)
        return K_lin, n

    def model2(self):
        '''

        Model 2: A -> B -> C ... -> Z

        Creates two arrays from the given reaction rate constants. One for the
        main diagonal of the matrix K, which corresponds to the loss in
        concentration for each species. The other one for the diagonal under
        the main diagonal, which corresponds to the gain in concentration for
        each species. Then generates the matrix K.

        In this model the last species does not react any further.

        Returns
        -------
        K_lin : np.array
            A 2D array which corresponds to the reaction rate constant matrix
            for a linear decay with n-species.

        '''
        k_hin = self.k
        k1 = np.array(k_hin) * (-1)
        k2 = k1.copy()*(-1)
        K_lin = np.diag(k2, k=-1)
        np.fill_diagonal(K_lin, k1)
        K_lin[-1, -1] = 0
        n = len(k_hin)+1
        return K_lin, n

    def model3(self):
        
        '''

        Model 3: A <=> B <=> C ... <=> Z -> 0

        Takes the two given arrays of reaction rate constants and generates the
        reaction matrix. The main diagonal is the loss of the species, the
        under main diagonal is the gain of the next species and the over main
        diagonal is the gain of the prior species.

        In this model the last species reacts into nothingness.

        Returns
        -------
        K_eq : np.array
            A 2D array which corresponds to the reaction rate constant matrix
            for an equilibrium reaction.

        '''
        # self.k[0] und self.k[1]?
        k_hin = self.k[:int(0.5*len(self.k)+0.5)]
        k_back = self.k[int(0.5*len(self.k)+0.5):]
        k1 = np.array(k_hin) * (-1)
        k1 = np.append(k1, [0])
        k2 = k1.copy()*(-1)
        k2 = np.delete(k2, -1)
        k3 = np.array(k_back)
        K_eq = np.diag(k2, k=-1)
        for i in range(len(k3)):
            K_eq[i, i+1] = k3[i]
        np.fill_diagonal(K_eq, k1)
        k4 = np.diagonal(K_eq, 1) * (-1)
        k5 = np.diagonal(K_eq)
        k4 = np.insert(k4, 0, 0)
        k4[-1] = 0
        k6 = k4 + k5
        np.fill_diagonal(K_eq, k6)
        K_eq[-1,-1] = -k_back[-1]-k_hin[-1]
        K_eq=K_eq[:-1, :-1]
        n = len(k_hin)
        return K_eq, n

    def model4(self):        
        '''

        Model 4: A <=> B <=> C ... <=> Z

        Takes the two given arrays of reaction rate constants and generates the
        reaction matrix. The main diagonal is the loss of the species, the
        under main diagonal is the gain of the next species and the over main
        diagonal is the gain of the prior species.

        In this model the last species does not react any further.

        Returns
        -------
        K_eq : np.array
            A 2D array which corresponds to the reaction rate constant matrix
            for an equilibrium reaction.

        '''
        k_hin = self.k[:int(0.5*len(self.k))]
        k_back = self.k[int(0.5*len(self.k)):]
        k1 = np.array(k_hin) * (-1)
        k1 = np.append(k1, [0])
        k2 = k1.copy()*(-1)
        k3 = np.array(k_back)
        K_eq = np.diag(k2, k=-1)
        for i in range(len(k3)):
            K_eq[i, i+1] = k3[i]
        np.fill_diagonal(K_eq, k1)
        K_eq[-1, -1] = 0
        k4 = np.diagonal(K_eq, 1) * (-1)
        k5 = np.diagonal(K_eq)
        k4 = np.insert(k4, 0, 0)
        k4[-1] = 0
        k6 = k4 + k5
        np.fill_diagonal(K_eq, k6)
        K_eq=K_eq[:-1, :-1]
        n = len(k_hin)+1
        return K_eq, n

    # Specific models

    def model5(self):
        '''

        Model 5: A -> B -> C -> D
                      B ------> D

        Creates two arrays from the given reaction rate constants. One for the
        main diagonal of the matrix K, which corresponds to the loss in
        concentration for each species. The other one for the diagonal under
        the main diagonal, which corresponds to the gain in concentration for
        each species. Adds the additional elements, which deviate from the
        normal linear pathway. Then generates the matrix K.

        In this model the last species does not react any further.
        ONLY four reaction rate constants are allowed.

        Returns
        -------
        K : np.array
            A 2D array which corresponds to the reaction rate constant matrix
            for an equilibrium reaction.

        '''
        k_hin = self.k
        k1 = np.array(k_hin) * (-1)
        k1[-1] = 0
        k2 = np.delete(np.array(k_hin), -1)
        K = np.diag(k2, k=-1)
        np.fill_diagonal(K, k1)
        K[1][1] = K[1][1] + k_hin[3] * (-1)
        K[3][1] = k_hin[3]
        n = 4
        return K, n

    def model6(self):
        '''

        Model 6: A -> B -> C -> D -> E
                      B -----------> E

        Creates two arrays from the given reaction rate constants. One for the
        main diagonal of the matrix K, which corresponds to the loss in
        concentration for each species. The other one for the diagonal under
        the main diagonal, which corresponds to the gain in concentration for
        each species. Adds the additional elements, which deviate from the
        normal linear pathway. Then generates the matrix K.

        In this model the last species does not react any further.
        ONLY five reaction rate constants are allowed.

        Returns
        -------
        K : np.array
            A 2D array which corresponds to the reaction rate constant matrix
            for an equilibrium reaction.

        '''
        k_hin = self.k
        k1 = np.array(k_hin) * (-1)
        k1[-1] = 0
        k2 = np.delete(np.array(k_hin), -1)
        K = np.diag(k2, k=-1)
        np.fill_diagonal(K, k1)
        K[1][1] = K[1][1] + k_hin[4] * (-1)
        K[4][1] = k_hin[4]
        n = 5
        return K, n

    def model7(self):
        '''

        Model 7: A -> B -> C -> D -> E
                           C ------> E

        Creates two arrays from the given reaction rate constants. One for the
        main diagonal of the matrix K, which corresponds to the loss in
        concentration for each species. The other one for the diagonal under
        the main diagonal, which corresponds to the gain in concentration for
        each species. Adds the additional elements, which deviate from the
        normal linear pathway. Then generates the matrix K.

        In this model the last species does not react any further.
        ONLY five reaction rate constants are allowed.

        Returns
        -------
        K : np.array
            A 2D array which corresponds to the reaction rate constant matrix
            for an equilibrium reaction.

        '''
        k_hin = self.k
        k1 = np.array(k_hin) * (-1)
        k1[-1] = 0
        k2 = np.delete(np.array(k_hin), -1)
        K = np.diag(k2, k=-1)
        np.fill_diagonal(K, k1)
        K[2][2] = K[2][2] + k_hin[4] * (-1)
        K[4][2] = k_hin[4]
        n = 5
        return K, n

    def model8(self):
        '''

        Model 8: A -> B -> C -> D -> E -> F
                           C -----------> F

        Creates two arrays from the given reaction rate constants. One for the
        main diagonal of the matrix K, which corresponds to the loss in
        concentration for each species. The other one for the diagonal under
        the main diagonal, which corresponds to the gain in concentration for
        each species. Adds the additional elements, which deviate from the
        normal linear pathway. Then generates the matrix K.

        In this model the last species does not react any further.
        ONLY six reaction rate constants are allowed.

        Returns
        -------
        K : np.array
            A 2D array which corresponds to the reaction rate constant matrix.

        '''
        k_hin = self.k
        k1 = np.array(k_hin) * (-1)
        k1[-1] = 0
        k2 = np.delete(np.array(k_hin), -1)
        K = np.diag(k2, k=-1)
        np.fill_diagonal(K, k1)
        K[2][2] = K[2][2] + k_hin[5] * (-1)
        K[5][2] = k_hin[5]
        n = 6
        return K, n

    def model9(self):
        '''

        Model 9: A -> B
                 A -> D

        Generates the matrix K.

        In this model the last species does not react any further.
        ONLY two reaction rate constants are allowed.

        Returns
        -------
        K : np.array
            A 2D array which corresponds to the reaction rate constant matrix.

        '''
        k_hin = self.k
        K = np.zeros((3, 3))
        K[0][0] = (k_hin[0] + k_hin[1]) * (-1)
        K[1][0] = k_hin[0]
        K[2][0] = k_hin[1]
        n = 3
        return K, n

    def model10(self):
        '''

        Model 10: A -> B
                       B -> C
                       B -> D

        Generates the matrix K.

        In this model the last species does not react any further.
        ONLY three reaction rate constants are allowed.

        Returns
        -------
        K : np.array
            A 2D array which corresponds to the reaction rate constant matrix.

        '''
        k_hin = self.k
        K = np.zeros((4, 4))
        K[0][0] = k_hin[0] * (-1)
        K[1][0] = k_hin[0]
        K[1][1] = (k_hin[1] + k_hin[2]) * (-1)
        K[2][1] = k_hin[1]
        K[3][1] = k_hin[2]
        n = 4
        return K, n
