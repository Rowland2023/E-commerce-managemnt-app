

export default function errorHandler(req,res,next){
    console.error(err.stack);
    return res.status(500).json({message:err.message})
}