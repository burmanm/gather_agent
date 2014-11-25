from gatherer import Gatherer

class mem(Gatherer):

    """
    Gather memory statistics 
    (add here free mem stuff that's calculated) using different meminfo stats
    """
    MEM_INFO = '/proc/meminfo'
    
    def gather(self):
        return self._fetch_mem_stat()
 
    def _fetch_mem_stat(self):
        lines = self._fetch_mem_stat_lines()
        results = []
        for line in lines:
            results.append(self._columns_to_event(line))
            
        return list(results)

    def _columns_to_event(self, columns):
        return self.create_event(columns[0][:-1].lower(), int(columns[1]))

    def _fetch_mem_stat_lines(self):
        with open(self.MEM_INFO, 'r') as f:
            for l in f:
                yield l.split()
    
