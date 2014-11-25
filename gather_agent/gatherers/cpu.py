from gatherer import Gatherer
import time

class cpu(Gatherer):
    """
    Catch CPU statistics..
    """
    last = None
    previous_stats = None
    STAT = '/proc/stat'

    def gather(self):
        results = []
        stats = self._fetch_cpu_stat()
        now = int(round(time.time()))

        if self.previous_stats is not None:
            diff = now - self.last

            for i, k in zip(stats, self.previous_stats):
                deltas = self._shift_stats(self._delta_stats(i, k), diff)
                for key, value in self._stat_columns_to_dict(deltas).iteritems():
                    results.append(self.create_event(key, value))

        self.last = now
        self.previous_stats = stats

        return list(results)

    def _stat_columns_to_dict(self, columns):
        key = columns[0]
        rdict = {}
        rdict[key + '.user'] = columns[1]
        rdict[key + '.nice'] = columns[2]
        rdict[key + '.system'] = columns[3]
        rdict[key + '.idle'] = columns[4]
        rdict[key + '.iowait'] = columns[5]
        rdict[key + '.irq'] = columns[6]
        rdict[key + '.softirq'] = columns[7]

        return rdict

    def _fetch_cpu_stat(self):
        with open(self.STAT, 'r') as f:
            result = []
            for l in f:
                if l.startswith('cpu'):
                    result.append(l.split())
                else:
                    return result

    def _shift_stats(self, stats, diff):
        for i in xrange(1, len(stats)):
            stats[i] = (stats[i] / diff)
            return stats        
                
    def _delta_stats(self, stats, previous_stats):
        result = []
        result.append(stats[0])
        for i in xrange(1, len(previous_stats)):            
            result.append(int(stats[i]) - int(previous_stats[i]))
        return result
