 //@C Copyright Notice
 //@C ================
 //@C This file is part of CPSW. It is subject to the license terms in the LICENSE.txt
 //@C file found in the top-level directory of this distribution and at
 //@C https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
 //@C
 //@C No part of CPSW, including this file, may be copied, modified, propagated, or
 //@C distributed except according to the terms contained in the LICENSE.txt file.

#include <int2dbl.h>
#include <cpsw_yaml.h>
#include <stdio.h>
#include <inttypes.h>

void
CInt2Dbl::checkArgs()
{
}

CInt2Dbl::CInt2Dbl(const CInt2Dbl &orig, Key &k)
: CIntEntryImpl(orig, k),
  scale_( orig.scale_ ),
  offset_( orig.offset_ ),
  intOffset_( orig.intOffset_ )
{
}

CInt2Dbl::CInt2Dbl(Key &k, YamlState &n)
: CIntEntryImpl(k, n),
  scale_(SCALE_DFLT),
  offset_(OFF_DFLT),
  intOffset_(INTOFF_DFLT)
{

	readNode(n, "scale",     &scale_);
	readNode(n, "offset",    &offset_);
	readNode(n, "intOffset", &intOffset_);

	checkArgs();
}

void
CInt2Dbl::dumpYamlPart(YAML::Node &n) const
{
	if ( scale_ != SCALE_DFLT )
		writeNode(n, "scale", scale_);
	if ( offset_ != OFF_DFLT )
		writeNode(n, "offset", offset_);
	if ( intOffset_ != INTOFF_DFLT )
		writeNode(n, "intOffset", intOffset_);
}

// create an adapter object (which may contain run-time state data)
EntryAdapt
CInt2Dbl::createAdapter(IEntryAdapterKey &key, Path path, const std::type_info& interfaceType) const
{
	if ( isInterface<DoubleVal>(interfaceType) ) {
		if ( RW != getMode() )
			throw InterfaceNotImplementedError("Double interface not supported (item is read- or write-only)");
		EntryAdapt ea = _createAdapter<shared_ptr<CInt2DblAdapt> >(this, path);
		return ea;
	} else if ( isInterface<DoubleVal_RO>(interfaceType) ) {
		if ( WO == getMode() )
			throw InterfaceNotImplementedError("Double_RO interface not supported (item is write-only)");
		return _createAdapter<shared_ptr<CInt2DblAdapt> >(this, path);
	}
#ifdef ALLOW_SCALVAL_ACCESS
	// delegate to superclass -- this allows the user to create
	// 'ScalVal' interfaces and access the raw bits as a ScalVal.
	// The user could also create a Stream interface.
	return CIntEntryImpl::createAdapter(key, path, interfaceType);
#else
	// This could be prohibited by not delegating to CIntEntryImpl
	// and either delegating to CEntryImpl (stream interface) or
	// returning a NULL shared-pointer (no other interfaces).
    //
    // HOWEVER: since CScalVal_ROAdapt/CScalVal_WOAdapt are bases of
	//          out adapters they could always use dynamic_pointer_cast() and
	//          obtain a ScalVal_RO/ScalVal interface handle.
	//          To avoid this 'loophole' we could create additional
	//          wrapper classes...
	return EntryAdapt();
#endif
}

// Actual uint64_t/int64_t <-> double conversion functions
void
CInt2Dbl_ROAdapt::int2dbl(double *dst, uint64_t *src, unsigned nelms)
{
ConstInt2Dbl entry = static_pointer_cast<ConstInt2Dbl::element_type>(ie_);
double     scale = entry->getScale();
double     off   = entry->getOffset();
uint64_t  ioff   = entry->getIntOffset();

	if ( isSigned() ) {
		int64_t sioff = ioff;
		for (unsigned i = 0; i <nelms; i++) {
			int64_t ival = src[i];
			dst[i] = ((double)(ival + sioff)) * scale + off;
		}
	} else {
		for (unsigned i = 0; i <nelms; i++) {
			uint64_t ival = src[i];
			dst[i] = ((double)(ival + ioff)) * scale + off;
		}
	}

}

void
CInt2Dbl_WOAdapt::dbl2int(uint64_t *dst, double *src, unsigned nelms)
{
ConstInt2Dbl entry = static_pointer_cast<ConstInt2Dbl::element_type>(ie_);

double     scale = entry->getScale();
double     off   = entry->getOffset();
uint64_t  ioff   = entry->getIntOffset();

uint64_t  shft   = entry->getSizeBits() - (entry->isSigned() ? 1 : 0 );

double    dlim   = exp2( shft );
uint64_t  imax   = shft >= 64 ? 0xffffffffffffffff : (((uint64_t)1) << shft) - 1;

	if ( isSigned() ) {
		double sioff = (int64_t)ioff;
		for (unsigned i = 0; i <nelms; i++) {
			double  dval = round( (src[i] - off) / scale ) - sioff;
			int64_t v;

			// saturate
			if ( dval >= dlim )
				v =  imax;
			else if ( dval < -dlim )
				v = ~imax;
			else if ( ( (( v = dval ) < 0) != (dval < 0) ) && v != 0 ) {
				v = dval > 0 ? imax : ~imax;
			}
				
			dst[i] = (uint64_t)v;
		}
	} else {
		double sioff = ioff;
		for (unsigned i = 0; i <nelms; i++) {
			double   dval = round( (src[i] - off) / scale ) - sioff;
			uint64_t v;

			// saturate
			if ( dval >= dlim )
				v = imax;
			else if ( dval < 0. )
				v = 0;
			else 
				v = dval;

			dst[i] = v;
		}
	}
}

CInt2Dbl_ROAdapt::CInt2Dbl_ROAdapt(Key &k, Path p, shared_ptr<const CInt2Dbl> ie)
: IIntEntryAdapt(k, p, ie),
  CScalVal_ROAdapt(k, p, ie)
{
}

CInt2Dbl_WOAdapt::CInt2Dbl_WOAdapt(Key &k, Path p, shared_ptr<const CInt2Dbl> ie)
: IIntEntryAdapt(k, p, ie),
  CScalVal_WOAdapt(k, p, ie)
{
}

CInt2DblAdapt::CInt2DblAdapt(Key &k, Path p, shared_ptr<const CInt2Dbl> ie)
: IIntEntryAdapt(k, p, ie),
  CScalVal_ROAdapt(k, p, ie),
  CInt2Dbl_ROAdapt(k, p, ie),
  CScalVal_WOAdapt(k, p, ie),
  CInt2Dbl_WOAdapt(k, p, ie)
{
} 

// register this class with the factory
DECLARE_YAML_FIELD_FACTORY(Int2Dbl);
