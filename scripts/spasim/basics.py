from pandas import DataFrame


class Demographics:
    """Data Container for demographics and their categories"""

    def __init__(self, var_code_cate: dict):
        self.var_code_cate = var_code_cate

    def select(self, variables):
        """only keep info of selected variables"""
        return Demographics({var: self.var_code_cate[var] for var in variables})

    @property
    def variables(self):
        return tuple(self.var_code_cate.keys())

    @property
    def shape(self):
        return tuple([len(self.var_code_cate[var]) for var in self.var_code_cate])


class Constraints(Demographics):
    """Data container for demographics and their marginal distributions"""

    def __init__(self, var_code_cate: dict, var_marg_dist: dict):
        super(Constraints, self).__init__(var_code_cate)
        self.var_marg_dist = var_marg_dist
        self._check_categorizing()

    def select(self, variables):
        """only keep info of selected variables"""
        return Constraints(var_code_cate={var: self.var_code_cate[var] for var in variables},
                           var_marg_dist={var: self.var_marg_dist[var] for var in variables})

    def _check_categorizing(self):
        for var in self.var_code_cate:
            if len(self.var_code_cate[var]) != len(self.var_marg_dist[var]):
                raise ValueError("The distribution structure of %s does not match with its categorizing" % var)

    @property
    def var_marg_dist_by_cate(self):
        dist = {}
        for var in self.variables:
            dist[var] = {self.var_code_cate[var][code]: round(self.var_marg_dist[var][code], 2) for code in
                         self.var_code_cate[var]}
        return dist


class Population:
    """Population in tabular form"""

    def __init__(self, demographics: Demographics, records, weights=None):
        self.demographics = demographics

        # the variable(column) order of record should be the same as the variable in demographics
        self.records = DataFrame(records, columns=demographics.variables)

        if weights is not None:
            if len(weights) == len(self.records):
                self.records["weights"] = weights
            else:
                raise ValueError("The length of weights must equal to the length of records")
        else:
            self.records["weights"] = 1 / len(self.records)

    def normalize_weights(self, total_weight=1):
        """Normalize weights so that the sum of all record's weights equals to 1"""
        self.records["weights"] /= sum(self.records["weights"])
        self.records["weights"] *= total_weight

    def aggregate(self):
        """Generate aggregate-form population"""
        columns = list(self.records.columns)
        columns.remove("weights")
        cate_weights = self.records.groupby(by=columns)["weights"].sum()

        return Population(self.demographics,
                          records=cate_weights.index.to_frame(index=False),
                          weights=cate_weights.to_list())

    def recode_variable(self, new_var_code_cate: dict, var_recode_map: dict):
        """Recode variable or reduce variable categories"""
        for var in var_recode_map:
            code_cate_convert_map = var_recode_map[var]
            for new_code in code_cate_convert_map:
                old_codes = code_cate_convert_map[new_code]
                self.records[var] = self.records[var].apply(
                    lambda old_code: new_code if old_code in old_codes else old_code)

        for var in new_var_code_cate:
            self.demographics.var_code_cate[var] = new_var_code_cate[var]

    def select(self, variables):
        """Generate a mew population with only selected attributes/variables"""
        return Population(demographics=self.demographics.select(variables),
                          records=self.records[variables],
                          weights=self.records["weights"])

    @property
    def variables(self):
        return self.demographics.variables

    @property
    def marginal_dist(self):
        dist = {}
        for var in self.demographics.variables:
            weights_by_code = self.records.groupby(var)["weights"].sum()
            weights_by_code = weights_by_code.to_dict()
            weights_by_cate_name = {self.demographics.var_code_cate[var][code]: round(weights_by_code[code], 2) for code
                                    in weights_by_code}
            dist[var] = weights_by_cate_name
        return dist
