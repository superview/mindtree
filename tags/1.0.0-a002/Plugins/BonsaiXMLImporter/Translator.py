unicodeTranslationMap = (
   # In this Pattern     replace           with this     replace      with this
   #                     this prefix                     this suffix
   # --------------      -----------       --------      -----------  ---------
     # Logic Symbols
   ( '\.\-\.',         ( '\.\-\.',         u'\u00AC'  ), None                  ),    # Negation              -        0172   0x00AC
   ( '\.\^\.',         ( '\.\^\.',         u'\u2227'  ), None                  ),    # Conjunction           .^.      8743   0x2227
   ( '\.v\.',          ( '\.v\.',          u'\u2228'  ), None                  ),    # Disjuntion            .v.      8744   0x2228
   ( '\.V\.',          ( '\.V\.',          u'\u2228'  ), None                  ),    # Disjuntion            .V.      8744   0x2228
   ( '\.\-&gt;\.',     ( '\.\-&gt;\.',     u'\u2192'  ), None                  ),    # Conditional           .->.     8594   0x2192
   ( '\.\-\>\.',       ( '\.\-\>\.',       u'\u2192'  ), None                  ),    # Conditional           .->.     8594   0x2192
   ( '\.&lt;\-&gt;\.', ( '\.&lt;\-&gt;\.', u'\u2194'  ), None                  ),    # Biconditional         .<->.    8596   0x2194
   ( '\.<\-\>\.',      ( '\.\<\-\>\.',     u'\u2194'  ), None                  ),    # Biconditional         .<->.    8596   0x2194
   ( '\.A\.',          ( '\.A\.',          u'\u2200'  ), None                  ),    # Universal             .A.      8704   0x2200
   ( '\.E\.',          ( '\.E\.',          u'\u2203'  ), None                  ),    # Existential           .E.      8707   0x2203
   ( '\.N\.',          ( '\.N\.',          u'\u25A1'  ), None                  ),    # Necessitation         .N.      9633   0x25A1
   ( '\.P\.',          ( '\.P\.',          u'\u25C7'  ), None                  ),    # Possibility           .P.      9671   0x25C7
   ( '\.\![A-Za-z]\.', ( '\.\!',           u'<u>'     ), ( '\.',      '</u>' ) ),    # Imperative            .!x.     underscore-x 
   ( '\.T\.',          ( '\.T\.',          u'\u22A4'  ), None                  ),    # Taugology             .T.      8868   0x22A4
   ( '\.T/\.',         ( '\.T/\.',         u'\u22A5'  ), None                  ),    # Contradiction         .T/.     8869   0x22A5
     
     # Meta-Logical Symbols
   ( '\.\|\-\.',       ( '\.\|\-\.',       u'\u22A6'  ), None                  ),    # Entailment            .|-.     8870   0x22A6
   ( '\.\|\-/\.',      ( '\.\|\-/\.',      u'\u22AC'  ), None                  ),    # Not Entailment            .|-.     8870   0x22A6
   ( '\.\|\=\.',       ( '\.\|\=\.',       u'\u22A7'  ), None                  ),    # Semantics             .|=.     8871   0x22A7
   ( '\.\/\^\.',       ( '\.\/\^\.',       u'<B>\u2234</B>'), None             ),    # Therefore
   ( '\/\^',           ( '\/\^',           u'<B>\u2234</B>'), None             ),    # Therefore             /^       8756   0x2234
   ( '\.VAL\.',        ( '\.VAL\.',        u'<I><B>V</B></I>' ), None          ),    # Valuation Function    V( P ) 

     # Set Theory Symbols
   ( '\.null\.',       ( '\.null\.',       u'\u2205'  ), None                  ),    # NULL                  .null.   8709   0x2205
   ( '\.in\.',         ( '\.in\.',         u'\u2208'  ), None                  ),    # Element of            .in.     8712   0x2208
   ( '\.in/\.',        ( '\.in/\.',        u'\u2209'  ), None                  ),    # Not element of        .in/.    8713   0x2209
   ( '\.set\^\.',      ( '\.set\^\.',      u'\u2229'  ), None                  ),    # Intersection          .set^.   8745   0x2229
   ( '\.setv\.',       ( '\.setv\.',       u'\u222A'  ), None                  ),    # Union                 .setv.   8746   0x222A
   ( '\.set&lt;\.',    ( '\.set&lt;\.',    u'\u2282'  ), None                  ),    # Subset                .set<.   8834   0x2282
   ( '\.set\<\.',      ( '\.set\<\.',      u'\u2282'  ), None                  ),    # Subset                .set<.   8834   0x2282
   ( '\.set&lt;\/\.',  ( '\.set&lt;\/\.',  u'\u2284'  ), None                  ),    # Not Subset            .set</.  8836   0x2284
   ( '\.set\<\/\.',    ( '\.set\<\/\.',    u'\u2284'  ), None                  ),    # Not Subset            .set</.  8836   0x2284
   ( '\.set&lt;\=\.',  ( '\.set&lt;\=\.',  u'\u2286'  ), None                  ),    # Propser Subset        .set<=.  8838   0x2286
   ( '\.set\<\=\.',    ( '\.set\<\=\.',    u'\u2286'  ), None                  ),    # Propser Subset        .set<=.  8838   0x2286
   ( '\.set&lt;\=\/\.',( '\.set&lt;\=\/\.',u'\u2288'  ), None                  ),    # Not Proper Subset     .set<=/. 8840   0x2288
   ( '\.set\<\=\/\.',  ( '\.set\<\=\/\.',  u'\u2288'  ), None                  ),    # Not Proper Subset     .set<=/. 8840   0x2288
   ( '\.set&gt;\.',    ( '\.set&gt;\.',    u'\u2283'  ), None                  ),    # Superset              .set>.   8835   0x2283
   ( '\.set\>\.',      ( '\.set\>\.',      u'\u2283'  ), None                  ),    # Superset              .set>.   8835   0x2283
   ( '\.set&gt;\/\.',  ( '\.set&gt;\/\.',  u'\u2285'  ), None                  ),    # Not Superset          .set>/.  8837   0x2285
   ( '\.set\>\/\.',    ( '\.set\>\/\.',    u'\u2285'  ), None                  ),    # Not Superset          .set>/.  8837   0x2285
   ( '\.set&gt;\=\.',  ( '\.set&gt;\=\.',  u'\u2287'  ), None                  ),    # Proper superset       .set>=.  8839   0x2287
   ( '\.set\>\=\.',    ( '\.set\>\=\.',    u'\u2287'  ), None                  ),    # Proper superset       .set>=.  8839   0x2287
   ( '\.set&gt;\=/\.', ( '\.set&gt;\=\.',  u'\u2289'  ), None                  ),    # Not Proper superset   .set>=.  8839   0x2287
   ( '\.set\>\=/\.',   ( '\.set\>\=\.',    u'\u2289'  ), None                  ),    # Not Proper superset   .set>=.  8839   0x2287
   ( '\.X\.',          ( '\.X\.',          u'\u00D7'  ), None                  ),    # Cross                 .X.      0215   0x00D7
      
     # Relational Symbols
   ( '\.&lt;\=\.',     ( '\.&lt;\=\.',     u'\u2264'  ), None                  ),    # Less or equal to      .<=.     8804   0x2264
   ( '\.\<\=\.',       ( '\.\<\=\.',       u'\u2264'  ), None                  ),    # Less or equal to      .<=.     8804   0x2264
   ( '\.&gt;\=\.',     ( '\.&gt;\=\.',     u'\u2265'  ), None                  ),    # Greater or eaul to    .>=.     8805   0x2265
   ( '\.\>\=\.',       ( '\.\>\=\.',       u'\u2265'  ), None                  ),    # Greater or eaul to    .>=.     8805   0x2265
   ( '=/',             ( '=/',             u'\u225D'  ), None                  ),    # Not equal to          =/       8800   0x225D
   ( '.=df.',          ( '.=df.',          u'\u225D'  ), None                  ),    # Definition            .=df.    8797   0x225D
   ( '=df',            ( '=df',            u'\u225D'  ), None                  ),    # Definition            =df
     
     # Other Symbols
   ( '\.3\=\.',        ( '\.3\=\.',        u'\u2261'  ), None                  ),    # Triple Equals         .3=.     8801   0x2261
     
     # Greek Letters
   ( '\.ALPHA\.',      ( '\.ALPHA\.',      u'\u0391'  ), None                  ),    # ALPHA                 .ALPHA.  0913   0x0391
   ( '\.BETA\.',       ( '\.BETA\.',       u'\u0392'  ), None                  ),    # BETA                  .BETA.   0914   0x0392
   ( '\.GAMMA\.',      ( '\.GAMMA\.',      u'\u0393'  ), None                  ),    # GAMMA                 .GAMMA.  0915   0x0393
   ( '\.DELTA\.',      ( '\.DELTA\.',      u'\u0394'  ), None                  ),    # DELTA                 .DELTA.  0916   0x0394
   ( '\.EPSILON\.',    ( '\.EPSILON\.',    u'\u0395'  ), None                  ),    # EPSILON               .EPSILON.0917   0x0395
   ( '\.ZETA\.',       ( '\.ZETA\.',       u'\u0396'  ), None                  ),    # ZETA                  .ZETA.   0918   0x0396
   ( '\.ETA\.',        ( '\.ETA\.',        u'\u0397'  ), None                  ),    # ETA                   .ETA.    0919   0x0397
   ( '\.THETA\.',      ( '\.THETA\.',      u'\u0398'  ), None                  ),    # THETA                 .THETA.  0920   0x0398
   ( '\.IOTA\.',       ( '\.IOTA\.',       u'\u0399'  ), None                  ),    # IOTA                  .IOTA.   0921   0x0399
   ( '\.KAPPA\.',      ( '\.KAPPA\.',      u'\u039A'  ), None                  ),    # KAPPA                 .KAPPA.  0922   0x039A
   ( '\.LAMBDA\.',     ( '\.LAMBDA\.',     u'\u039B'  ), None                  ),    # LAMBDA                .LAMBDA. 0923   0x039B
   ( '\.MU\.',         ( '\.MU\.',         u'\u039C'  ), None                  ),    # MU                    .MU.     0924   0x039C
   ( '\.NU\.',         ( '\.NU\.',         u'\u039D'  ), None                  ),    # NU                    .NU.     0925   0x039D
   ( '\.XI\.',         ( '\.XI\.',         u'\u039E'  ), None                  ),    # XI                    .XI.     0926   0x039E
   ( '\.OMICRON\.',    ( '\.OMICRON\.',    u'\u039F'  ), None                  ),    # OMICRON               .OMICRON.0927   0x039F
   ( '\.PI\.',         ( '\.PI\.',         u'\u03A0'  ), None                  ),    # PI                    .PI.     0928   0x03A0
   ( '\.RHO\.',        ( '\.RHO\.',        u'\u03A1'  ), None                  ),    # RHO                   .RHO.    0929   0x03A1
   ( '\.SIGMA\.',      ( '\.SIGMA\.',      u'\u03A3'  ), None                  ),    # SIGMA                 .SIGMA.  0931   0x03A3
   ( '\.TAU\.',        ( '\.TAU\.',        u'\u03A4'  ), None                  ),    # TAU                   .TAU.    0932   0x03A4
   ( '\.UPSILON\.',    ( '\.UPSILON\.',    u'\u03A5'  ), None                  ),    # UPSILON               .UPSILON.0933   0x03A5
   ( '\.PHI\.',        ( '\.PHI\.',        u'\u03A6'  ), None                  ),    # PHI                   .PHI.    0934   0x03A6
   ( '\.CHI\.',        ( '\.CHI\.',        u'\u03A7'  ), None                  ),    # CHI                   .CHI.    0935   0x03A7
   ( '\.PSI\.',        ( '\.PSI\.',        u'\u03A8'  ), None                  ),    # PSI                   .PSI.    0936   0x03A8
   ( '\.OMEGA\.',      ( '\.OMEGA\.',      u'\u03A9'  ), None                  ),    # OMEGA                 .OMEGA.  0937   0x03A9

   ( '\.alpha\.',      ( '\.alpha\.',      u'\u03B1'  ), None                  ),    # alpha                 .alpha.  0945   0x03B1
   ( '\.beta\.',       ( '\.beta\.',       u'\u03B2'  ), None                  ),    # beta                  .beta.   0946   0x03B2
   ( '\.gamma\.',      ( '\.gamma\.',      u'\u03B3'  ), None                  ),    # gamma                 .gamma.  0947   0x03B3
   ( '\.delta\.',      ( '\.delta\.',      u'\u03B4'  ), None                  ),    # delta                 .delta.  0948   0x03B4
   ( '\.epsilon\.',    ( '\.epsilon\.',    u'\u03B5'  ), None                  ),    # epsilon               .epsilon.0949   0x03B5
   ( '\.zeta\.',       ( '\.zeta\.',       u'\u03B6'  ), None                  ),    # zeta                  .zeta.   0950   0x03B6
   ( '\.eta\.',        ( '\.eta\.',        u'\u03B7'  ), None                  ),    # eta                   .eta.    0951   0x03B7
   ( '\.theta\.',      ( '\.theta\.',      u'\u03B8'  ), None                  ),    # theta                 .theta.  0952   0x03B8
   ( '\.iota\.',       ( '\.iota\.',       u'\u03B9'  ), None                  ),    # iota                  .iota.   0953   0x03B9
   ( '\.kappa\.',      ( '\.kappa\.',      u'\u03BA'  ), None                  ),    # kappa                 .kappa.  0954   0x03BA
   ( '\.lambda\.',     ( '\.lambda\.',     u'\u03BB'  ), None                  ),    # lambda                .lambda. 0955   0x03BB
   ( '\.mu\.',         ( '\.mu\.',         u'\u03BC'  ), None                  ),    # mu                    .mu.     0956   0x03BC
   ( '\.nu\.',         ( '\.nu\.',         u'\u03BD'  ), None                  ),    # nu                    .nu.     0957   0x03BD
   ( '\.xi\.',         ( '\.xi\.',         u'\u03BE'  ), None                  ),    # xi                    .xi.     0958   0x03BE
   ( '\.omicron\.',    ( '\.omicron\.',    u'\u03BF'  ), None                  ),    # omicron               .omicron.0959   0x03BF
   ( '\.pi\.',         ( '\.pi\.',         u'\u03C0'  ), None                  ),    # pi                    .pi.     0960   0x03C0
   ( '\.rho\.',        ( '\.rho\.',        u'\u03C1'  ), None                  ),    # rho                   .rho.    0961   0x03C1
   ( '\.sigma\.',      ( '\.sigma\.',      u'\u03C2'  ), None                  ),    # sigma                 .sigma.  0962   0x03C2
   ( '\.sigma2\.',     ( '\.sigma2\.',     u'\u03C3'  ), None                  ),    # sigma2                .sigma2. 0963   0x03C3
   ( '\.tau\.',        ( '\.tau\.',        u'\u03C4'  ), None                  ),    # tau                   .tau.    0964   0x03C4
   ( '\.upsilon\.',    ( '\.upsilon\.',    u'\u03C5'  ), None                  ),    # upsilon               .upsilon.0965   0x03C5
   ( '\.phi\.',        ( '\.phi\.',        u'\u03C6'  ), None                  ),    # phi                   .phi.    0966   0x03C6
   ( '\.chi\.',        ( '\.chi\.',        u'\u03C7'  ), None                  ),    # chi                   .chi.    0967   0x03C7
   ( '\.psi\.',        ( '\.psi\.',        u'\u03C8'  ), None                  ),    # psi                   .psi.    0968   0x03C8
   ( '\.omega\.',      ( '\.omega\.',      u'\u03C9'  ), None                  ),    # omega                 .omega.  0969   0x03C9
   )

import re

class TranslationEntry:
   def __init__( self, entry ):
      self._envRegEx    = re.compile( entry[0] )
      
      self._prefixRegEx = re.compile( entry[1][0] )
      self._prefixSubst = entry[1][1]
      
      if entry[2]:
         self._suffixRegEx = re.compile( entry[2][0] )
         self._suffixSubst = entry[2][1]
      else:
         self._suffixRegEx = None
         self._suffixSubst = None

   def translate( self, aString ):
      if self._suffixRegEx:
         match = self._envRegEx.search( aString )
         while match:
            sliceBeg, sliceEnd = match.span( )
            
            preSliceBeg, preSliceEnd = self._prefixRegEx.match( aString, sliceBeg, sliceEnd ).span( )
            sufSliceBeg, sufSliceEnd = self._suffixRegEx.search( aString, sliceBeg+1, sliceEnd ).span( )
               #TODO:  This code should really check to make sure the slice
               # matched to the reg exp is really at the end of envSlice.
               # if not, it should try searching for a new match.
               
            aString = ''.join( ( aString[ : preSliceBeg ], self._prefixSubst, aString[ preSliceEnd : sufSliceBeg ], self._suffixSubst, aString[ sufSliceEnd : ] ) )
            
            match = self._envRegEx.search( aString, preSliceBeg )
      else:
         aString = self._envRegEx.sub( self._prefixSubst, aString )
         
      return aString

class Translator:
   ###################
   ## Standard Methods
   def __init__( self ):
      # Rebuild the unicodeTranslationMap, compiling all the regular expressions
      self._map      = [ ]
      
      for entry in unicodeTranslationMap:
         self._map.append( TranslationEntry( entry ) )

   ############
   ## Extension
   def translate( self, line ):
      for trans in self._map:
         line = trans.translate( line )
         
      return line

#testData = '.!x.'

#t = Translator( )
#out = t.translate( testData )
#pass

