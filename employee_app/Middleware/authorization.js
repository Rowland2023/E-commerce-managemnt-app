

export default function authorization(req,res,next){
    try{
        const {user}= req;
        const {resources} = req;

        const isOwner = resources?.OwnerId === user?.id
        const isOwnwerAdmin = user?.roll === 'Admin';
        if(isOwner || isOwnwerAdmin){
            return next();
        }
        else{
            return res.status(404).json({message:"Forbidden:Insufficient right"})
        }
    }catch(err){
        console.error(err.stack);
        return res.status(500).json({message: err.message})
    }
}