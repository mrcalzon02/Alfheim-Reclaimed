package com.continuityworks.alfheimcompanion.worldgen;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class HarborSiteTest {
    @Test void boundedSearchHonorsColumnCapAcrossAllAttempts() {
        var calls=new java.util.concurrent.atomic.AtomicInteger();
        var result=HarborSite.findBounded(0,0,64,(x,z)-> {calls.incrementAndGet();return coast(0).sample(x,z);},
            HarborGeometry.PARTS,()->0L,2,1000);
        assertTrue(result.site().isEmpty());assertEquals("column_budget",result.outcome());assertEquals(2,calls.get());
    }
    @Test void expiredBudgetDoesNotStartANativeColumn() {
        var time=new java.util.concurrent.atomic.AtomicLong();var calls=new java.util.concurrent.atomic.AtomicInteger();
        var result=HarborSite.findBounded(0,0,64,(x,z)-> {calls.incrementAndGet();return coast(0).sample(x,z);},
            HarborGeometry.PARTS,()->time.getAndAdd(10),32,10);
        assertTrue(result.site().isEmpty());assertEquals("time_budget",result.outcome());assertEquals(0,calls.get());
    }
    @Test void slowColumnStopsWithoutTryingAnotherOrientation() {
        var time=new java.util.concurrent.atomic.AtomicLong();var calls=new java.util.concurrent.atomic.AtomicInteger();
        var result=HarborSite.findBounded(0,0,64,(x,z)-> {calls.incrementAndGet();time.addAndGet(100);return coast(0).sample(x,z);},
            HarborGeometry.PARTS,time::get,32,10);
        assertTrue(result.site().isEmpty());assertEquals("time_budget",result.outcome());assertEquals(1,calls.get());
    }
    @Test void boundedGenerationAllowsUnsampledFitDefectsInEveryOrientation() {
        for(int r=0;r<4;r++) {
            var base=coast(r);int[] defect=HarborGeometry.rotate(12,12,r);
            HarborSite.Sampler terrain=(x,z)->x==defect[0]&&z==defect[1]?new HarborSite.Column(80,80,false):base.sample(x,z);
            assertTrue(HarborSite.find(0,0,64,terrain).isEmpty());
            var result=HarborSite.findBounded(0,0,64,terrain,HarborGeometry.PARTS,()->0L,32,1000);
            assertEquals(r,result.site().orElseThrow().rotation());assertTrue(result.columns()<=22);
        }
    }
    @Test void boundedCentersStillRejectGrossVoid() {
        var base=coast(0);
        var result=HarborSite.findBounded(0,0,64,(x,z)->x==70&&z==23?new HarborSite.Column(0,0,false):base.sample(x,z),
            HarborGeometry.PARTS,()->0L,32,1000);
        assertTrue(result.site().isEmpty());
    }
    private HarborSite.Sampler coast(int r) {
        return (x,z)-> {
            int[] local=HarborGeometry.rotate(x,z,(4-r)%4);
            return local[1]<0?new HarborSite.Column(64,60,true):new HarborSite.Column(65,65,false);
        };
    }
    @Test void facesUsableWaterInEachDirection() {
        for(int r=0;r<4;r++) assertEquals(r,HarborSite.find(0,0,64,coast(r)).orElseThrow().rotation());
    }
    @Test void rejectsInlandAndOpenOcean() {
        assertTrue(HarborSite.find(0,0,64,(x,z)->new HarborSite.Column(65,65,false)).isEmpty());
        assertTrue(HarborSite.find(0,0,64,(x,z)->new HarborSite.Column(64,60,true)).isEmpty());
    }
    @Test void rejectsDeepSeabedAndHighRelief() {
        assertTrue(HarborSite.find(0,0,64,(x,z)->z<0?new HarborSite.Column(64,45,true):new HarborSite.Column(65,65,false)).isEmpty());
        assertTrue(HarborSite.find(0,0,64,(x,z)->z<0?new HarborSite.Column(64,60,true):new HarborSite.Column(80,80,false)).isEmpty());
    }
    @Test void findsSingleColumnHazardsBetweenCoarseSamples() {
        var base=coast(0);
        assertTrue(HarborSite.find(0,0,64,(x,z)->x==12&&z==12?null:base.sample(x,z)).isEmpty());
        assertTrue(HarborSite.find(0,0,64,(x,z)->x==12&&z==12?new HarborSite.Column(80,80,false):base.sample(x,z)).isEmpty());
        assertTrue(HarborSite.find(0,0,64,(x,z)->x==12&&z==-12?new HarborSite.Column(64,40,true):base.sample(x,z)).isEmpty());
    }
    @Test void supportedShoreApronAcceptsACurvedBoundary() {
        assertTrue(HarborSite.find(0,0,64,(x,z)->z<Math.sin(x/12.0)*8?new HarborSite.Column(64,60,true):new HarborSite.Column(65,65,false)).isPresent());
    }
    @Test void shoreApronDoesNotAdmitDeepWaterOrBlockedWaterline() {
        var base=coast(0);
        assertTrue(HarborSite.find(0,0,64,(x,z)->x==0&&z==0?new HarborSite.Column(64,40,true):base.sample(x,z)).isEmpty());
        assertTrue(HarborSite.find(0,0,64,(x,z)->x==0&&z==0?new HarborSite.Column(65,65,true):base.sample(x,z)).isEmpty());
    }
    @Test void higherBankSelectsMatchingExtraFoundations() {
        var site=HarborSite.find(0,0,64,(x,z)->z<0?new HarborSite.Column(64,60,true):new HarborSite.Column(69,69,false)).orElseThrow();
        assertEquals(2,site.quayLift());assertEquals(60,site.baseY());
        assertEquals(58,site.baseY()-site.quayLift());
    }
    @Test void reclaimedQuayStillHasAnInlandApproach() {
        assertTrue(HarborSite.find(0,0,64,(x,z)->z<20?new HarborSite.Column(64,60,true):new HarborSite.Column(65,65,false)).isPresent());
        assertTrue(HarborSite.find(0,0,64,(x,z)->z>=90?new HarborSite.Column(64,60,true):coast(0).sample(x,z)).isEmpty());
    }
    @Test void lowDryBankIsLimitedByActualFootingReach() {
        for(int floor:new int[]{58,61,63}) {
            var site=HarborSite.find(0,0,64,(x,z)->z<0?new HarborSite.Column(64,60,true):new HarborSite.Column(floor,floor,false)).orElseThrow();
            assertEquals(0,site.quayLift());assertEquals(58,site.baseY());
        }
        assertTrue(HarborSite.find(0,0,64,(x,z)->z<0?new HarborSite.Column(64,60,true):new HarborSite.Column(57,57,false)).isEmpty());
        var base=coast(0);
        assertTrue(HarborSite.find(0,0,64,(x,z)->x==12&&z==12?new HarborSite.Column(57,57,false):base.sample(x,z)).isEmpty());
    }
    @Test void proposedConnectedFootprintsFaceTheCoastInEveryDirection() {
        for(String name:new String[]{"shipping","narrow_docks","inland_temple","narrow_docks_inland_temple","core_with_approach"})
            for(int r=0;r<4;r++)
                assertEquals(r,HarborSite.find(0,0,64,coast(r),HarborFootprintProposals.get(name)).orElseThrow().rotation());
        assertNull(HarborFootprintProposals.get("unknown"));
    }
    @Test void compactProposalExcludesRemovedDockButChecksEveryRetainedColumn() {
        var compact=HarborFootprintProposals.get("narrow_docks_inland_temple");var base=coast(0);
        HarborSite.Sampler removed=(x,z)->x==1&&z==-65?new HarborSite.Column(64,40,true):base.sample(x,z);
        assertTrue(HarborSite.find(0,0,64,removed).isEmpty());
        assertTrue(HarborSite.find(0,0,64,removed,compact).isPresent());
        HarborSite.Sampler retained=(x,z)->x==13&&z==-49?new HarborSite.Column(64,40,true):base.sample(x,z);
        assertTrue(HarborSite.find(0,0,64,retained,compact).isEmpty());
    }
    @Test void plannedCoreKeepsRequiredMembersAndExcludesOptionalDrydock() {
        var core=HarborFootprintProposals.get("core_with_approach");
        var names=java.util.Arrays.stream(core).map(HarborGeometry.Part::name).collect(java.util.stream.Collectors.toSet());
        assertEquals(java.util.Set.of("harbor_exchange","wavebreak_pier","harbormaster_house","quay_court","harbor_approach"),names);
        var base=coast(0);
        HarborSite.Sampler optional=(x,z)->x==13&&z==-49?new HarborSite.Column(64,40,true):base.sample(x,z);
        assertTrue(HarborSite.find(0,0,64,optional,core).isPresent());
        assertTrue(HarborSite.find(0,0,64,(x,z)->x==12&&z==12?null:base.sample(x,z),core).isEmpty());
    }
    @Test void intermediatePassRejectsBeforeAnExpensiveDenseWalk() {
        var visited=new java.util.HashSet<String>();var base=coast(0);
        var site=HarborSite.find(0,0,64,(x,z)-> {
            visited.add(x+","+z);
            return x==4&&z==4?new HarborSite.Column(80,80,false):base.sample(x,z);
        },HarborFootprintProposals.get("core_with_approach"));
        assertTrue(site.isEmpty());
        assertTrue(visited.size()<250,"Intermediate hazard should reject early: "+visited.size());
    }
    @Test void successfulRefinementStillVisitsEveryFootprintColumn() {
        for(String name:new String[]{"shipping","narrow_docks_inland_temple","core_with_approach"}) {
            var visited=new java.util.HashSet<String>();var parts=HarborFootprintProposals.get(name);var base=coast(0);
            assertTrue(HarborSite.find(0,0,64,(x,z)-> {visited.add(x+","+z);return base.sample(x,z);},parts).isPresent());
            for(var part:parts)for(int x=part.minX();x<=part.maxX();x++)for(int z=part.minZ();z<=part.maxZ();z++)
                assertTrue(visited.contains(x+","+z),"Unchecked column "+x+","+z);
        }
    }
    @Test void auditRecordsTheActualRejectionColumn() {
        var attempts=new java.util.ArrayList<HarborSite.Attempt>();var base=coast(0);
        assertTrue(HarborSite.find(0,0,64,(x,z)->x==1&&z==1?new HarborSite.Column(57,57,false):base.sample(x,z),
                HarborFootprintProposals.get("core_with_approach"),attempts::add).isEmpty());
        var first=attempts.get(0);assertFalse(first.accepted());
        assertEquals(0,first.rotation());assertEquals(0,first.lift());
        assertEquals(1,first.lastX());assertEquals(1,first.lastZ());assertEquals(57,first.lastColumn().floor());
    }
}
