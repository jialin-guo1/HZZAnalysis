from ROOT import *
from deltaR import *
from array import array

infile_name = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/ANATree/testfiles/test_CHS_VBF.root"
outfile_name = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/fileout/test_CHS_VBFgen.root"

infile = TFile(infile_name)
tree = infile.Get("Ana/passedEvents")

outfile = TFile(outfile_name,'recreate')
outTree = TTree("passedEvents","passedEvents")

H1_pt = array('f',[-1.0])
H1_eta = array('f',[-1.0])
H1_phi = array('f',[-1.0])
H1_mass = array('f',[-1.0])
H2_pt = array('f',[-1.0])
H2_eta = array('f',[-1.0])
H2_phi = array('f',[-1.0])
H2_mass = array('f',[-1.0])
H_dR = array('f',[-1.0])
passedGENH = array('i',[0])

H1_Mom_pt = array('f',[-1.0])
H1_Mom_eta = array('f',[-1.0])
H1_Mom_phi = array('f',[-1.0])
H1_Mom_mass = array('f',[-1.0])
H2_Mom_pt = array('f',[-1.0])
H2_Mom_eta = array('f',[-1.0])
H2_Mom_phi = array('f',[-1.0])
H2_Mom_mass = array('f',[-1.0])
H_Mom_dR = array('f',[-1.0])

H1_Mom_H_dR = array('f',[-1.0])
H2_Mom_H_dR = array('f',[-1.0])

matched_genjet1_dr = array('f',[-1.0])
matched_genjet2_dr = array('f',[-1.0])

matched_genjet1_pt= array('f',[-1.0])
matched_genjet1_eta= array('f',[-1.0])
matched_genjet1_phi= array('f',[-1.0])
matched_genjet1_mass= array('f',[-1.0])
matched_genjet2_pt= array('f',[-1.0])
matched_genjet2_eta= array('f',[-1.0])
matched_genjet2_phi= array('f',[-1.0])
matched_genjet2_mass= array('f',[-1.0])
matched_genjet12_dr= array('f',[-1.0])



H1_Bro_pt = std.vector(double)()
H1_Bro_eta = std.vector(double)()
H1_Bro_phi = std.vector(double)()
H1_Bro_mass = std.vector(double)()
H2_Bro_pt = std.vector(double)()
H2_Bro_eta = std.vector(double)()
H2_Bro_phi = std.vector(double)()
H2_Bro_mass = std.vector(double)()
H1_Bro_DR = std.vector(double)()
H2_Bro_DR = std.vector(double)()
H_Bro_DR12 = std.vector(double)()

H1_Mom_bro_dR = std.vector(double)()
H2_Mom_bro_dR = std.vector(double)()


outTree.Branch("H1_pt",H1_pt,"H1_pt/F")
outTree.Branch("H1_eta",H1_eta,"H1_eta/F")
outTree.Branch("H1_phi",H1_phi,"H1_phi/F")
outTree.Branch("H1_mass",H1_mass,"H1_mass/F")
outTree.Branch("H2_pt",H2_pt,"H2_pt/F")
outTree.Branch("H2_eta",H2_eta,"H2_eta/F")
outTree.Branch("H2_phi",H2_phi,"H2_phi/F")
outTree.Branch("H2_mass",H2_mass,"H2_mass/F")
outTree.Branch("H_dR",H_dR,"H_dR/F")
outTree.Branch("passedGENH",passedGENH,"passedGENH/O")

outTree.Branch("H_Mom_dR",H_Mom_dR,"H_Mom_dR/F")
outTree.Branch("H1_Mom_pt",H1_Mom_pt,"H1_Mom_pt/F")
outTree.Branch("H1_Mom_eta",H1_Mom_eta,"H1_Mom_eta/F")
outTree.Branch("H1_Mom_phi",H1_Mom_phi,"H1_Mom_phi/F")
outTree.Branch("H1_Mom_mass",H1_Mom_mass,"H1_Mom_mass/F")
outTree.Branch("H2_Mom_pt",H2_Mom_pt,"H2_Mom_pt/F")
outTree.Branch("H2_Mom_eta",H2_Mom_eta,"H2_Mom_eta/F")
outTree.Branch("H2_Mom_phi",H2_Mom_phi,"H2_Mom_phi/F")
outTree.Branch("H2_Mom_mass",H1_Mom_mass,"H2_Mom_mass/F")

outTree.Branch("H1_Bro_pt",H1_Bro_pt,"H1_Bro_pt/F")
outTree.Branch("H1_Bro_eta",H1_Bro_eta,"H1_Bro_eta/F")
outTree.Branch("H1_Bro_phi",H1_Bro_phi,"H1_Bro_phi/F")
outTree.Branch("H1_Mom_bro_dR",AddressOf(H1_Mom_bro_dR),"H1_Mom_bro_dR/F")
outTree.Branch("H2_Mom_bro_dR",AddressOf(H2_Mom_bro_dR),"H2_Mom_bro_dR/F")

outTree.Branch("H1_Mom_H_dR",H1_Mom_H_dR,"H1_Mom_H_dR/F")
outTree.Branch("H2_Mom_H_dR",H2_Mom_H_dR,"H2_Mom_H_dR/F")

outTree.Branch("matched_genjet1_dr",matched_genjet1_dr,"matched_genjet1_dr/F")
outTree.Branch("matched_genjet2_dr",matched_genjet2_dr,"matched_genjet2_dr/F")

outTree.Branch("matched_genjet1_pt",matched_genjet1_pt,"matched_genjet1_pt/F")
outTree.Branch("matched_genjet1_eta",matched_genjet1_eta,"matched_genjet1_pt/F")
outTree.Branch("matched_genjet1_phi",matched_genjet1_phi,"matched_genjet1_pt/F")
outTree.Branch("matched_genjet1_mass",matched_genjet1_mass,"matched_genjet1_pt/F")
outTree.Branch("matched_genjet2_pt",matched_genjet1_pt,"matched_genjet1_pt/F")
outTree.Branch("matched_genjet2_eta",matched_genjet2_eta,"matched_genjet2_eta/F")
outTree.Branch("matched_genjet2_phi",matched_genjet2_phi,"matched_genjet2_phi/F")
outTree.Branch("matched_genjet2_mass",matched_genjet2_mass,"matched_genjet2_mass/F")
outTree.Branch("matched_genjet12_dr",matched_genjet12_dr,"matched_genjet12_dr/F")



for ievent, event in enumerate(tree):
    H = []
    H_Mom_q = []
    H_bro = []
    findH = 0
    ngen_q = event.GEN_q_id.size()
    for i in range(0,ngen_q):
        if(abs(event.GEN_q_id[i])>6): continue
        if(event.GEN_q_status[i]==1): continue
        ndau = event.GEN_q_nDaughters[i]

        isH = False
        temp_bros = []
        for j in range(0,ndau):
            if(event.GEN_qdau_id[i][j]==25 and event.GEN_qdau_status[i][j]!=1):
                temp_H = TLorentzVector()
                temp_H.SetPtEtaPhiM(event.GEN_qdau_pt[i][j],event.GEN_qdau_eta[i][j],event.GEN_qdau_phi[i][j],event.GEN_qdau_mass[i][j])
                H.append(temp_H)
                findH += 1
                isH = True
            else:
                #print "this bro pt = "+str(event.GEN_qdau_pt[i][j])
                temp_bro = TLorentzVector()
                temp_bro.SetPtEtaPhiM(event.GEN_qdau_pt[i][j],event.GEN_qdau_eta[i][j],event.GEN_qdau_phi[i][j],event.GEN_qdau_mass[i][j])
                temp_bros.append(temp_bro)


        if(isH):
            temp_H_Mom = TLorentzVector()
            temp_H_Mom.SetPtEtaPhiM(event.GEN_q_pt[i],event.GEN_q_eta[i],event.GEN_q_phi[i],event.GEN_q_mass[i],)
            H_Mom_q.append(temp_H_Mom)
            H_bro.append(temp_bros)

    if(findH==2):
        passedGENH[0] = True
        H1_pt[0] = H[0].Pt()
        H1_eta[0] = H[0].Eta()
        H1_phi[0] = H[0].Phi()
        H1_mass[0] = H[0].M()
        H2_pt[0] = H[1].Pt()
        H2_eta[0] = H[1].Eta()
        H2_phi[0] = H[1].Phi()
        H2_mass[0] = H[1].M()

        H1_Mom_pt[0]=(H_Mom_q[0].Pt())
        H1_Mom_eta[0]=(H_Mom_q[0].Eta())
        H1_Mom_phi[0]=(H_Mom_q[0].Phi())
        H1_Mom_mass[0]=(H_Mom_q[0].M())
        H2_Mom_pt[0]=(H_Mom_q[1].Pt())
        H2_Mom_eta[0]=(H_Mom_q[1].Eta())
        H2_Mom_phi[0]=(H_Mom_q[1].Phi())
        H2_Mom_mass[0]=(H_Mom_q[1].M())

        H1_Bro_pt.push_back(H_bro[0][0].Pt())
        H1_Bro_eta.push_back(H_bro[0][0].Eta())
        H1_Bro_phi.push_back(H_bro[0][0].Phi())



        temp_dr = deltaR(H[0].Eta(),H[0].Phi(),H[1].Eta(),H[1].Phi())
        H_dR[0]=temp_dr

        temp_dr = deltaR(H_Mom_q[0].Eta(),H_Mom_q[0].Phi(),H_Mom_q[1].Eta(),H_Mom_q[1].Phi())
        H_Mom_dR[0] = temp_dr

        temp_dr = deltaR(H_Mom_q[0].Eta(),H_Mom_q[0].Phi(),H[0].Eta(),H[0].Phi())
        H1_Mom_H_dR[0] = temp_dr

        temp_dr = deltaR(H_Mom_q[1].Eta(),H_Mom_q[1].Phi(),H[1].Eta(),H[1].Phi())
        H2_Mom_H_dR[0] = temp_dr

        for bros in H_bro[0]:
            temp_dr = deltaR(H_Mom_q[0].Eta(),H_Mom_q[0].Phi(),bros.Eta(),bros.Phi())
            H1_Mom_bro_dR.push_back(temp_dr)

        for bros in H_bro[1]:
            temp_dr = deltaR(H_Mom_q[1].Eta(),H_Mom_q[1].Phi(),bros.Eta(),bros.Phi())
            H2_Mom_bro_dR.push_back(temp_dr)

        #find genjet
        matched_dr=[-1.0,-1.0]
        matched_index = [-1.0,-1.0]
        ngenjet = event.GENjet_pt.size()
        if(ngenjet<2): continue
        matched1 = False
        matched2 = False
        for iMon,Mom in enumerate(H_Mom_q):
            ngenjet = event.GENjet_pt.size()
            min_dr = 9999.999
            for i in range(0,ngenjet):
                temp_dr = deltaR(Mom.Eta(),Mom.Phi(),event.GENjet_eta[i],event.GENjet_phi[i])
                #print "this dr = "+str(temp_dr)
                if(temp_dr<min_dr and temp_dr<0.8):
                    min_dr = temp_dr
                    matched_dr[iMom] = temp_dr
                    matched_index[iMon] = i
                    #print "i = "+str(i)
                    if(iMon==0): matched1 = True
                    if(iMon==1): matched1 = True


        if(matched1 and matched2):
            print "matched"
            matched_genjet1_dr[0] = matched_dr[0]
            matched_genjet2_dr[0] = matched_dr[1]
            matched_genjet1_pt[0] = event.GENjet_pt[matched_index[0]]
            matched_genjet1_eta[0] = event.GENjet_eta[matched_index[0]]
            matched_genjet1_phi[0] = event.GENjet_phi[matched_index[0]]
            matched_genjet1_mass[0] = event.GENjet_mass[matched_index[0]]
            matched_genjet2_pt[0] = event.GENjet_pt[matched_index[1]]
            matched_genjet2_eta[0] = event.GENjet_eta[matched_index[1]]
            matched_genjet2_phi[0] = event.GENjet_phi[matched_index[1]]
            matched_genjet2_mass[0] = event.GENjet_mass[matched_index[1]]

            matched_genjet12_dr[0] = deltaR(matched_genjet1_eta,matched_genjet1_phi,matched_genjet2_eta,matched_genjet2_phi)



    outTree.Fill()










outfile.cd()
outTree.Write()
