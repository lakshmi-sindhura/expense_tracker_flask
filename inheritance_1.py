class father:
    def skill(self):
        print("coding")
class mother:
    def talent(self):
        print("cooking")
class child(father,mother):
    def parents(self):
        print("Inherited")
c=child()
c.skill()
c.talent()
c.parents()