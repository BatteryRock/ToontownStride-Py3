from toontown.building import DistributedVPElevatorAI
from toontown.building import FADoorCodes
from toontown.building.DistributedBoardingPartyAI import DistributedBoardingPartyAI
from toontown.coghq.DistributedFactoryElevatorExtAI import DistributedFactoryElevatorExtAI
from toontown.hood import CogHQAI
from toontown.suit import DistributedSellbotBossAI
from toontown.suit import DistributedSuitPlannerAI
from toontown.toonbase import ToontownGlobals

class SellbotHQAI(CogHQAI.CogHQAI):
    def __init__(self, air):
        super().__init__(air, ToontownGlobals.SellbotHQ, ToontownGlobals.SellbotLobby, FADoorCodes.SB_DISGUISE_INCOMPLETE,
                         DistributedVPElevatorAI.DistributedVPElevatorAI, DistributedSellbotBossAI.DistributedSellbotBossAI)
        self.factoryElevators = []
        self.factoryBoardingParty = None
        self.suitPlanners = []
        self.startup()

    def startup(self):
        super().startup()
        self.cogHQDoors = [self.extDoor] + [self.makeCogHQDoor(self.lobbyZoneId, 0, i + 1, self.lobbyFADoorCode) for i in range(3)]
        self.createFactoryElevators()
        if simbase.config.GetBool('want-boarding-groups', True):
            self.createFactoryBoardingParty()
        if simbase.config.GetBool('want-suit-planners', True):
            self.createSuitPlanners()
        for sp in self.suitPlanners:
            if sp.zoneId == self.zoneId:
                sp.cogHQDoors = self.cogHQDoors

    def createFactoryElevators(self):
        self.factoryElevators = [DistributedFactoryElevatorExtAI(self.air, self.air.factoryMgr, ToontownGlobals.SellbotFactoryInt, i)
                                 .generateWithRequired(ToontownGlobals.SellbotFactoryExt) for i in range(2)]
        fatalElevator = DistributedFactoryElevatorExtAI(self.air, self.air.factoryMgr, ToontownGlobals.SellbotFatalInt, 2)
        fatalElevator.generateWithRequired(ToontownGlobals.SellbotFactoryExt)
        self.factoryElevators.append(fatalElevator)

    def createFactoryBoardingParty(self):
        factoryIdList = [elevator.doId for elevator in self.factoryElevators]
        self.factoryBoardingParty = DistributedBoardingPartyAI(self.air, factoryIdList, 4)
        self.factoryBoardingParty.generateWithRequired(ToontownGlobals.SellbotFactoryExt)

    def createSuitPlanners(self):
        self.suitPlanners = [DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, self.zoneId)
                             .generateWithRequired(self.zoneId).d_setZoneId(self.zoneId).initTasks()]
        self.air.suitPlanners[self.zoneId] = self.suitPlanners[0]

        suitPlanner = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, ToontownGlobals.SellbotFactoryExt)
        suitPlanner.generateWithRequired(ToontownGlobals.SellbotFactoryExt).d_setZoneId(ToontownGlobals.SellbotFactoryExt).initTasks()
        self.suitPlanners.append(suitPlanner)
        self.air.suitPlanners[ToontownGlobals.SellbotFactoryExt] = suitPlanner

