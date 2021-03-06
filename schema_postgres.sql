SET TIME ZONE INTERVAL '+00:00';

DROP TABLE IF EXISTS to_planning_app;
CREATE TABLE to_planning_app (
  folderYear CHAR(10) NOT NULL,
  folderSequence CHAR(10) NOT NULL,
  folderSection CHAR(10) NOT NULL,
  folderRevision CHAR(10) NOT NULL,
  folderType CHAR(10) NOT NULL,
  communityInfo CHAR(255) DEFAULT NULL,
  folderDescription text,
  folderRsn INT DEFAULT NULL,
  folderTypeDesc CHAR(255) DEFAULT NULL,
  folderTypeList text DEFAULT NULL,
  geoID INT DEFAULT NULL,
  inDate CHAR(100) DEFAULT NULL,
  location CHAR(100) DEFAULT NULL,
  mainProperty INT DEFAULT NULL,
  maxOutcome INT DEFAULT NULL,
  propX REAL DEFAULT NULL,
  propY REAL DEFAULT NULL,
  referenceFile CHAR(255) DEFAULT NULL,
  statutoryInfo CHAR(255) DEFAULT NULL,
  subType CHAR(255) DEFAULT NULL,
  plannerName CHAR(255) DEFAULT NULL,
  plannerPhone CHAR(255) DEFAULT NULL,
  legalDesc CHAR(255) DEFAULT NULL,
  planningWard INT DEFAULT NULL,
  postal CHAR(10) DEFAULT NULL,
  propertyRoll CHAR(255) DEFAULT NULL,
  propertyRsn INT DEFAULT NULL,
  region CHAR(100) DEFAULT NULL,
  proposal CHAR(100) DEFAULT NULL,
  proposal_bachelor INT DEFAULT NULL,
  proposal_bedroom1 INT DEFAULT NULL,
  proposal_bedroom2 INT DEFAULT NULL,
  proposal_bedroom3plus INT DEFAULT NULL,
  proposal_condo INT DEFAULT NULL,
  proposal_existingBuildings INT DEFAULT NULL,
  proposal_existingNonResGFA INT DEFAULT NULL,
  proposal_existingResidGFA INT DEFAULT NULL,
  proposal_existingResUnits INT DEFAULT NULL,
  proposal_existingStoreys INT DEFAULT NULL,
  proposal_existingTotal INT DEFAULT NULL,
  proposal_folderRsn INT DEFAULT NULL,
  proposal_freehold INT DEFAULT NULL,
  proposal_proposedBuildings INT DEFAULT NULL,
  proposal_proposedGFA INT DEFAULT NULL,
  proposal_proposedLandUse CHAR(100) DEFAULT NULL,
  proposal_proposedNonResGFA INT DEFAULT NULL,
  proposal_proposedResidGFA INT DEFAULT NULL,
  proposal_proposedResUnits INT DEFAULT NULL,
  proposal_proposedStoreys INT DEFAULT NULL,
  proposal_proposedTotalGFA INT DEFAULT NULL,
  proposal_rental INT DEFAULT NULL,
  proposal_rooms INT DEFAULT NULL,
  proposal_totalGrossFloorArea INT DEFAULT NULL,
  proposal_totalNonResGFA INT DEFAULT NULL,
  proposal_totalResidGFA INT DEFAULT NULL,
  proposal_other INT DEFAULT NULL,
  maxStage INT DEFAULT NULL,
  maxStage_folderRsn INT DEFAULT NULL,
  maxStage_stageFlag INT DEFAULT NULL,
  maxStage_stageRsn INT DEFAULT NULL,
  maxStage_stageCode INT DEFAULT NULL,
  maxStage_stageCodeDesc CHAR(100) DEFAULT NULL,
  maxStage_stageDate CHAR(100) DEFAULT NULL,
  maxStage_maxStageOutcome CHAR(100) DEFAULT NULL,
  maxStageOutcome_applicationRsn INT DEFAULT NULL,
  maxStageOutcome_applicationTypeDesc CHAR(100) DEFAULT NULL,
  maxStageOutcome_comments text,
  maxStageOutcome_decisionDesc CHAR(255) DEFAULT NULL,
  maxStageOutcome_outcomeCode INT DEFAULT NULL,
  maxStageOutcome_outcomeDate CHAR(40) DEFAULT NULL,
  maxStageOutcome_outcomeDesc CHAR(100) DEFAULT NULL,
  maxStageOutcome_outcomeRsn CHAR(100) DEFAULT NULL,
  maxStageOutcome_stageDesc CHAR(100) DEFAULT NULL,
  maxStageOutcome_statusLinkFlag CHAR(100) DEFAULT NULL,
  plannerInfo CHAR(100) DEFAULT NULL,
  plannerInfo_plannerPhone CHAR(100) DEFAULT NULL,
  plannerInfo_plannerName CHAR(100) DEFAULT NULL,
  plannerInfo_plannerTitle CHAR(100) DEFAULT NULL,
  plannerInfo_emailAddress CHAR(100) DEFAULT NULL,
  propertyView_postal CHAR(100) DEFAULT NULL,
  propertyView_planningDistrict CHAR(100) DEFAULT NULL,
  propertyView_province CHAR(100) DEFAULT NULL,
  propertyView_propertyRsn INT DEFAULT NULL,
  propertyView_street CHAR(100) DEFAULT NULL,
  propertyView_planningWard INT DEFAULT NULL,
  propertyView_folders INT DEFAULT NULL,
  propertyView_city CHAR(100) DEFAULT NULL,
  propertyView_streetDirection CHAR(100) DEFAULT NULL,
  propertyView_streetType CHAR(100) DEFAULT NULL,
  propertyView_address CHAR(100) DEFAULT NULL,
  propertyView_wardDesc CHAR(100) DEFAULT NULL,
  propertyView_region CHAR(100) DEFAULT NULL,
  propertyView_legalDesc CHAR(200) DEFAULT NULL,
  propertyView_propertyRoll CHAR(100) DEFAULT NULL,
  propertyView_house CHAR(100) DEFAULT NULL,
  detaillink CHAR(100) DEFAULT NULL,
  ward_queried INT DEFAULT NULL,
  app_typ CHAR(100) DEFAULT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
  lastUpdated  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  geom geography(POINT,4326),
  PRIMARY KEY (folderYear,folderSequence,folderSection,folderRevision,folderType)
);

