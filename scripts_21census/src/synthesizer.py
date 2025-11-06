from .basics import Population, Constraints
import random


class Synthesizer:

    def __init__(self, base_population: Population, constraints: Constraints):
        self.base_population = base_population
        self.constraints = constraints
        self.synthetic_population = None

    def abs_error(self, synthetic_population=None):
        """Calculate absolute error of a synthetic population"""
        if synthetic_population is None:
            if self.synthetic_population is None:
                synthetic_population = self.base_population
            else:
                synthetic_population = self.synthetic_population

        error = 0
        for var in self.constraints.variables:
            dist_by_code = self.constraints.var_marg_dist[var]
            weights_by_code = synthetic_population.records.groupby(var)["weights"].sum()
            for cate_code in dist_by_code:
                error += abs(weights_by_code[cate_code] - dist_by_code[cate_code])

        return error

    def describe_results(self):
        print("Finial absolute error: ", self.abs_error())
        print("Initial Marginal Distribution: \n", self.base_population.marginal_dist)
        print("Constrained Marginal Distribution: \n", self.constraints.var_marg_dist_by_cate)
        print("Synthetic Marginal Distribution: \n", self.synthetic_population.marginal_dist)


class IPF(Synthesizer):
    """Synthesis based on Iterative Proportional Fitting - Deterministic Method"""

    def __init__(self, base_population: Population, constraints: Constraints):
        super(IPF, self).__init__(base_population, constraints)

    def synthesize(self, max_iter=50, stop_threshold=0.01):

        # initialize synthetic population
        self.synthetic_population = Population(self.base_population.demographics,
                                               self.base_population.records,
                                               weights=self.base_population.records["weights"])
        # IPF procedure
        for _ in range(max_iter):

            for var in self.constraints.variables:
                dist_by_code = self.constraints.var_marg_dist[var]
                weights_by_code = self.synthetic_population.records.groupby(var)["weights"].sum()
                new_weights = self.synthetic_population.records.apply(
                    lambda row: row["weights"] * dist_by_code[row[var]] / weights_by_code[row[var]] if weights_by_code[row[var]] >= 1e-6 else 0,
                    axis=1)
                self.synthetic_population.records["weights"] = new_weights

            self.synthetic_population.normalize_weights()

            if self.abs_error() <= stop_threshold:
                break

        return self.synthetic_population


class SA(Synthesizer):
    """Synthesis based on Simulated Annealing - stochastic method"""

    def __init__(self, base_population: Population, constraints: Constraints, synthesis_size):
        super(SA, self).__init__(base_population, constraints)
        self.synthesis_size = synthesis_size

    def synthesize(self, max_iter=100, init_temperature=100, stop_threshold=0.01, synthesis_size=None):
        # initialize synthetic population
        if synthesis_size is not None:
            self.synthesis_size = synthesis_size

        # simulated annealing procedure
        current_pop = Population(self.base_population.demographics,
                                 self.base_population.records.sample(self.synthesis_size))

        best_pop = current_pop
        best_error = self.abs_error(best_pop)

        for iter_num in range(max_iter):
            current_error = self.abs_error(current_pop)
            new_pop = self.gen_new_syn_pop(current_pop)
            new_error = self.abs_error(new_pop)
            temperature = (iter_num / max_iter) * init_temperature

            if new_error < current_error:
                current_pop = new_pop
                if new_error < best_error:
                    best_pop = new_pop
                    best_error = new_error
            else:
                if pow(2.71828, (current_error - new_error) * temperature) >= random.random():
                    current_pop = new_pop

            if best_error <= stop_threshold:
                break

        self.synthetic_population = best_pop

        return self.synthetic_population

    def gen_new_syn_pop(self, pop):
        new_pop = Population(pop.demographics,
                             pop.records,
                             weights=pop.records["weights"])

        new_ind = self.base_population.records.sample(1)
        new_ind["weights"] = 1 / self.synthesis_size
        replaced_ind_index = random.randint(0, self.synthesis_size - 1)
        new_pop.records.iloc[replaced_ind_index] = new_ind
        return new_pop
