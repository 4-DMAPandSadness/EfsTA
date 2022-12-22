# General linear models for any amount of species

# Model 1: A -> B -> C ... -> Z -> 0
# Model 2: A -> B -> C ... -> Z

# Specific linear models for a certain amount of species, with splits

# Model 3: A -> B -> C -> D; B -> D
# Model 4: A -> B -> C -> D -> E; B -> E
# Model 5: A -> B -> C -> D -> E; C -> E
# Model 6: A -> B -> C -> D -> E -> F; C -> F
# Model 7: A -> B; A -> C
# Model 8: A -> B ; B -> C ; B -> D

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
        return K, n

    def model1(self):
        '''

        Model 1: A -> B -> C ... -> Z -> 0

        Creates two arrays from the given reaction rate constants. One for the
        main diagonal of the matrix K, which corresponds to the loss in
        concentration for each species. The other one for the diagonal under
        the main diagonal, which corresponds to the gain in concentration for
        each following species. Then generates the matrix K.

        In this model the last species decays back to the groundstate.

        Returns
        -------
        K : np.array
            A 2D array which corresponds to the reaction rate constant matrix
            for a linear decay with n-species.

        '''
        k_main_diagonal = np.array(self.k) * (-1)
        k_lower_diagonal = k_main_diagonal.copy()*(-1)
        k_lower_diagonal = np.delete(k_lower_diagonal, -1)
        K = np.diag(k_lower_diagonal, k=-1)
        np.fill_diagonal(K, k_main_diagonal)
        n = len(self.k)
        return K, n

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
        K : np.array
            A 2D array which corresponds to the reaction rate constant matrix
            for a linear decay with n-species.

        '''
        k_main_diagonal = np.array(self.k) * (-1)
        k_lower_diagonal = k_main_diagonal.copy()*(-1)
        K = np.diag(k_lower_diagonal, k=-1)
        np.fill_diagonal(K, k_main_diagonal)
        K[-1, -1] = 0
        n = len(self.k)+1
        return K, n

    # Specific models

    def model3(self):
        '''

        Model 3: A -> B -> C -> D
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
        
        k_main_diagonal = np.array(self.k) * (-1)
        k_main_diagonal[-1] = 0
        k_lower_diagonal = np.delete(np.array(self.k), -1)
        K = np.diag(k_lower_diagonal, k=-1)
        np.fill_diagonal(K, k_main_diagonal)
        K[1][1] = K[1][1] + self.k[3] * (-1)
        K[3][1] = self.k[3]
        n = 4
        return K, n

    def model4(self):
        '''

        Model 4: A -> B -> C -> D -> E
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
        
        k_main_diagonal = np.array(self.k) * (-1)
        k_main_diagonal[-1] = 0
        k_lower_diagonal = np.delete(np.array(self.k), -1)
        K = np.diag(k_lower_diagonal, k=-1)
        np.fill_diagonal(K, k_main_diagonal)
        K[1][1] = K[1][1] + self.k[4] * (-1)
        K[4][1] = self.k[4]
        n = 5
        return K, n

    def model5(self):
        '''

        Model 5: A -> B -> C -> D -> E
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
        
        k_main_diagonal = np.array(self.k) * (-1)
        k_main_diagonal[-1] = 0
        k_lower_diagonal = np.delete(np.array(self.k), -1)
        K = np.diag(k_lower_diagonal, k=-1)
        np.fill_diagonal(K, k_main_diagonal)
        K[2][2] = K[2][2] + self.k[4] * (-1)
        K[4][2] = self.k[4]
        n = 5
        return K, n

    def model6(self):
        '''

        Model 6: A -> B -> C -> D -> E -> F
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
        
        k_main_diagonal = np.array(self.k) * (-1)
        k_main_diagonal[-1] = 0
        k_lower_diagonal = np.delete(np.array(self.k), -1)
        K = np.diag(k_lower_diagonal, k=-1)
        np.fill_diagonal(K, k_main_diagonal)
        K[2][2] = K[2][2] + self.k[5] * (-1)
        K[5][2] = self.k[5]
        n = 6
        return K, n

    def model7(self):
        '''

        Model 9: A -> B
                 A -> C

        Generates the matrix K.

        In this model the last species does not react any further.
        ONLY two reaction rate constants are allowed.

        Returns
        -------
        K : np.array
            A 2D array which corresponds to the reaction rate constant matrix.

        '''
        
        K = np.zeros((3, 3))
        K[0][0] = (self.k[0] + self.k[1]) * (-1)
        K[1][0] = self.k[0]
        K[2][0] = self.k[1]
        n = 3
        return K, n

    def model8(self):
        '''

        Model 8: A -> B
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
        
        K = np.zeros((4, 4))
        K[0][0] = self.k[0] * (-1)
        K[1][0] = self.k[0]
        K[1][1] = (self.k[1] + self.k[2]) * (-1)
        K[2][1] = self.k[1]
        K[3][1] = self.k[2]
        n = 4
        return K, n
