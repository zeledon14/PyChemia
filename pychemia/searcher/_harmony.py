import random
from pychemia import pcm_log
from _searcher import Searcher


class HarmonySearch(Searcher):
    def __init__(self, population, params=None, fraction_evaluated=0.95, generation_size=32, stabilization_limit=10):
        """
        Harmony Search Method:
        This searcher is the simplest one, does not require a metric space except for the evaluation
        of duplicates. It is more elaborated than a simple random search.
        Harmony Search only requires changers for existing members and generation of new random members.

        :param population: A subclass of the ABC Population
        :param params: (dict) Parameters to setup the Searcher
                    hmcr: Harmony Memory Considering Rate, how often a value should be discarded in favor of new random
                          members, a value of 1 means never discard any member except those in tail (see below).
                          A value of 0 means always discard except those in tail (see below).
                    par:  Probability of being changed for those not discarded.
                          A value of 1 means always changed, a value of 0 means never changed.
                    top:  Number of members that are automatically promoted to the next generation (The best)
                    tail: Number of members that are automatically discarded (The worst)
        :param stabilization_limit: Number of generations survived by the best member
        :param fraction_evaluated: The ratio between the active members evaluated and the total number of members.
                                   Once this ratio is fulfilled the generation is considered sufficient to start a cycle
        """
        # Mandatory objects
        Searcher.__init__(self, population, fraction_evaluated, generation_size, stabilization_limit)
        # Parameters
        self.hmcr = None  # harmony_memory_considering_rate
        self.par = None
        self.top = None
        self.tail = None
        self.set_params(params)
        self.delta_change = 1

    def set_params(self, params):
        """
        Set the parameters for the Harmony Search algorithm
        There are 4 parameters

        :param params:
        """
        self.hmcr = 0.9
        self.par = 0.9
        self.top = 2
        self.tail = 2
        if params is None:
            params = {}
        if 'hmcr' in params:
            self.hmcr = params['hmcr']
        if 'par' in params:
            self.par = params['par']
        if 'top' in params:
            self.top = params['top']
        if 'tail' in params:
            self.tail = params['tail']
        assert (1.0 >= self.hmcr >= 0.0)
        assert (1.0 >= self.par >= 0.0)

    def get_params(self):
        return {'hmcr': self.hmcr, 'par': self.par}

    def run_one(self):
        """
        Run one cycle for the Harmony Search Method
        """
        # Get a static selection of the values in the generation that are evaluated
        selection = self.population.ids_sorted(self.population.actives_evaluated)
        pcm_log.debug('Size of selection : %d' % len(selection))

        # Automatic promotion for the top ranking members
        for entry_id in selection[:self.top]:
            pcm_log.debug('[HS](%s) Top entry: promoted' % str(entry_id))
            self.pass_to_new_generation(entry_id, reason='Top %d' % self.top)
        # assert(len(self.get_generation(self.current_generation+1)) >= 2)

        # Intermediate members, their fate depends on hmcr and par
        for entry_id in selection[self.top:-self.tail]:
            rnd = random.random()
            pcm_log.debug('[HS](%s) Middle entry: rnd=%4.3f hmcr= %4.3f' % (entry_id, rnd, self.hmcr))
            if rnd <= self.hmcr:
                rnd = random.random()
                if rnd < self.par:
                    pcm_log.debug('[HS](%s) Promoted (modified): rnd= %4.3f < par= %4.3f' % (entry_id, rnd, self.par))
                    self.replace_by_changed(entry_id, reason='rnd= %4.3f < par= %4.3f' % (rnd, self.par))
                else:
                    pcm_log.debug('[HS](%s) Promoted (unmodified): rnd= %4.3f >= par= %4.3f' %
                                  (entry_id, rnd, self.par))
                    self.pass_to_new_generation(entry_id, reason='rnd= %4.3f >= par= %4.3f' % (rnd, self.par))
            else:
                pcm_log.debug('[HS](%s) Discarded: rnd= %4.3f > hmcr= %4.3f ' % (entry_id, rnd, self.hmcr))
                self.replace_by_random(entry_id, reason='rnd= %4.3f > hmcr= %4.3f' % (rnd, self.hmcr))
        # assert(len(self.get_generation(self.current_generation+1)) <= self.generation_size-2)

        for entry_id in selection[-self.tail:]:
            pcm_log.debug('[HS](%s) Tail entry: discarded' % entry_id)
            self.replace_by_random(entry_id, reason='Tail %d' % self.tail)
            # assert(len(self.get_generation(self.current_generation+1)) == self.generation_size)
